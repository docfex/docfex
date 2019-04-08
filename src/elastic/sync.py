from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search
from src.config.config import base_path, dir_breaks, supp_mime_types, root_web_path, folder_group
from .models import markdown, folder, pdf, audio, video, base
from .setup import get_es_indices, es_client
from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import Lock, Event
from datetime import datetime
import logging
import mimetypes
import asyncio
import os


es_sync_scheduler = BackgroundScheduler()
sync_lock = Lock()
end_event = Event()
es_job_id = 'es_sync'


class EndEventError(Exception):
    '''
    Exception that must be raised, when an end_event is set
    '''
    def __init__(self, message, error=None):
        self.message = message
        self.error = error
        super(EndEventError, self).__init__(message)


def close_scheduler():
    '''
    Sets the end_event and shutsdown the scheduler after all jobs returned
    '''
    if not(end_event.is_set()):
        end_event.set()
    logging.info('end scheduler')
    if es_sync_scheduler.running:
        es_sync_scheduler.shutdown(wait=True)


def sync_elastic(app, update_indices=[]):
    '''
    Syncs the elastic server with the os.
    :param update_indices: Can be used to update certain types inside elasticsearch (like pdf, folder,...).
    :type update_indices: List[str] 
    '''
    try:
        if end_event.is_set():
            raise EndEventError('end requested before execution')
        with sync_lock:
            logging.info('sync elastic')
            synced_items = []
            with app.app_context():
                for path, folders, files in os.walk(base_path):
                    web_path = root_web_path[:-1] + path.replace(base_path, '').replace(dir_breaks,'/')
                    previous_path = web_path if web_path != root_web_path[:-1] else root_web_path

                    saved_folders = asyncio.run(_sync_folders(folders, path, web_path, previous_path, update_indices))
                    saved_files = asyncio.run(_sync_files(files, path, web_path, previous_path, update_indices))
                    synced_items += saved_folders + saved_files

                    if end_event.is_set():
                        raise EndEventError('end requested in os.walk-loop')

            asyncio.run(_delete_moved_items(synced_items))
    except (EndEventError) as error:
        logging.warning(error.message)
        raise


async def _delete_moved_items(valid_items):
    '''
    Delete items that are in elastic, but not anymore on the os
    '''
    es_indices = get_es_indices()
    if not(valid_items):
        # no items saved -> os is empty, drop elastic
        s = Search(index=es_indices).query('match_all')
        s = s.source(include=['web_path'])
        _delete_doc_by_query(s)
        return

    # make sure all docs are searchable
    timeout = 0
    valid_items_searchable = False
    while not(valid_items_searchable) and timeout < 20:
        for v_item in valid_items:
            if end_event.is_set():
                raise EndEventError('end requested while deleting items')
            
            s = Search(index=es_indices).query('term', web_path=v_item)
            if s.count() > 0:
                valid_items_searchable = True
            else:
                valid_items_searchable = False
                await asyncio.sleep(1)
                timeout += 1
                break    
    # create search here again to prevent versionerror in elastic
    s = Search(index=es_indices)
    s = s.source(include=['web_path'])
    for v_item in valid_items:
        s = s.exclude('term', web_path=v_item)
    _delete_doc_by_query(s)


def _delete_doc_by_query(setup_search):
    '''
    Executes the built query to delete all matches
    '''
    res = setup_search.execute()
    if not(res):
        return
    for h in res:
        logging.warning('Deleting doc ' + h.web_path)
    setup_search.delete()


def _get_mtime_as_utc_iso_str(os_path):
    '''
    Returns the modified time of a os path in 'utc iso' format
    '''
    mtime = datetime.utcfromtimestamp(os.path.getmtime(os_path))
    return mtime.isoformat(timespec='seconds')


def _get_type_size(os_path):
    '''
    returns the size of a os path
    '''
    return os.path.getsize(os_path)


def _is_es_different(es_doc, doc):
    '''
    Returns True when os doc differs to elastic doc
    '''
    return ((es_doc.os_size != doc.own_doc.os_size) or (es_doc.last_modified != doc.own_doc.last_modified))


async def _sync_folders(folders, os_path, web_path, previous_path, update_indices):
    '''
    Synchronises os folders with elastic
    '''
    force_update = folder_group in update_indices
    saved_folders = []
    for f in folders:
        if end_event.is_set():
            raise EndEventError('end requested in folder-loop')

        cmb_web_path = web_path + '/' + f
        abs_os_path = os_path + dir_breaks + f
        mtime = _get_mtime_as_utc_iso_str(abs_os_path)
        f_size = _get_type_size(abs_os_path)
        es_folder = folder.EsFolder(
            name=f, web_path=cmb_web_path, parent_path=previous_path, last_modified=mtime, os_size=f_size, mimetype='')
        saved = await _save_doc(es_folder, force_update)
        saved_folders.append(cmb_web_path)
        if not(saved):
            logging.error(es_folder.own_obj.web_path + 'couldn\'t be saved')
    
    return saved_folders  


async def _sync_files(files, os_path, web_path, previous_path, update_indices):
    '''
    Synchronises os files of supported mimetypes with elastic
    '''
    saved_files = []
    for f in files:
        if end_event.is_set():
            raise EndEventError('end requested in file-loop')

        cmb_web_path = web_path + '/' + f
        abs_os_path = os_path + dir_breaks + f
        mtime = _get_mtime_as_utc_iso_str(abs_os_path)
        f_size = _get_type_size(abs_os_path)
        for types in supp_mime_types['markdown']:
            mimetypes.add_type(types,'.md')
        file_type = mimetypes.guess_type(f, strict=False)[0]  
        if file_type in supp_mime_types['markdown']:
            es_file = markdown.EsMarkdown(name=f, web_path=cmb_web_path, parent_path=previous_path, mimetype=file_type,
                                          full_filename=abs_os_path, last_modified=mtime, os_size=f_size)
        elif file_type in supp_mime_types['pdf']:
            es_file = pdf.EsPdf(name=f, web_path=cmb_web_path, parent_path=previous_path, mimetype=file_type,
                                full_filename=abs_os_path, last_modified=mtime, os_size=f_size)
        elif file_type in supp_mime_types['audio']:
            es_file = audio.EsAudio(name=f, web_path=cmb_web_path, mimetype=file_type,
                                    parent_path=previous_path, last_modified=mtime, os_size=f_size)
        elif file_type in supp_mime_types['video']:
            es_file = video.EsVideo(name=f, web_path=cmb_web_path, mimetype=file_type,
                                    parent_path=previous_path, last_modified=mtime, os_size=f_size)
        else:
            # skip not supported file types
            continue

        force_update = es_file.own_index in update_indices
        saved = await _save_doc(es_file, force_update)
        saved_files.append(cmb_web_path)
        if not(saved):
            logging.error(es_file.own_obj.web_path + 'couldn\'t be saved')
            
    return saved_files
        

async def _save_doc(doc, force_update=False):
    '''
    Saves document if os is different than elastic
    '''
    if not(force_update) and doc.exists():
        es_doc = doc.get(_source_include=['last_modified', 'os_size'])
        if not(_is_es_different(es_doc, doc)):
            # elastic already up to date
            return True
            
    doc.save()
    saved = await _doc_saved(doc)
    if saved:
        logging.info('Successfully saved doc ' + doc.own_obj.web_path)
    return saved


async def _doc_saved(doc):
    '''
    Returns True when the document is saved and can be searched in elastic
    '''
    doc_found = False
    timeout = 0
    while (doc_found == False) and (timeout < 20):
        if end_event.is_set():
            raise EndEventError('end requested while saving item')

        doc_found = doc.exists()
        if not(doc_found):
            await asyncio.sleep(1)
            timeout += 1
    return doc_found



