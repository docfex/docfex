from flask import render_template, Markup, send_from_directory, url_for, session, request, abort, current_app
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Search
from src.config.config import base_path, dir_breaks, SECRET_KEY, recent_topic_len, flask_hostname, flask_port, root_web_path, file_upload_path
from src.topics import topics, folder_group, file_group
from src.elastic.setup import ElasticSettings, es_client
from src.elastic.sync import sync_elastic
from src.elastic.models.attachments import attachment_fields
from src.search import get_search_result, SearchSettings
from src.header import header
from src.elastic.sync import es_sync_scheduler, close_scheduler
from elasticsearch.exceptions import TransportError
from urllib3.exceptions import NewConnectionError
from functools import wraps
from gevent.pywsgi import WSGIServer
import logging
import sys
import re
import os
import json


def start_flask(debug=False):
    '''
    Registers all request functions and starts the flask-app.
    Runs flask_shutdown() when flask is shutdown
    '''
    logging.info("Starting flask ...")
    app = current_app._get_current_object()
    app.secret_key = SECRET_KEY
    app.static_folder = 'src/static'
    app.template_folder = 'src/templates'
    app.before_request(before_request)
    app.add_url_rule(root_web_path + 'favicon.ico', 'favicon', favicon)
    app.add_url_rule(root_web_path, 'home', home)
    app.add_url_rule(root_web_path + file_upload_path + '/<path:file_and_path>', 'get_local_file', get_local_file)
    app.add_url_rule(root_web_path + 'fakeEmbed/<path:file_and_path>', 'get_embed_file', get_embed_file)
    app.add_url_rule(root_web_path + 'Settings', 'settings', settings, methods=['POST', 'GET'])
    app.add_url_rule(root_web_path + '<path:subpath>', 'sub_pages', sub_pages)
    # use for quick debugging
    #app.run(debug=debug, use_reloader=False)
    #flask_shutdown()
    try:
        WSGIServer((flask_hostname, flask_port), app).serve_forever()
    except KeyboardInterrupt:
        pass
    finally:    
        flask_shutdown()


def favicon():
    app = current_app._get_current_object()
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def flask_shutdown():
    '''
    Contains functions that will be called when flask shuts down
    '''
    close_scheduler()


def get_recent_topics():
    '''
    Returns a list of recently viewed files inside the active session
    '''
    recent_topics = []
    if len(session['recent']) != 0:
        recent_topics = session['recent'][:]
    
    return recent_topics 

def add_to_recent_topics(current_topic):
    '''
    Adds the current topic to the recently viewed list
    '''
    if len(session['recent']) >= recent_topic_len:
        session['recent'] = session['recent'][1:] + [current_topic]
    else:
        session['recent'].append(current_topic)

def remove_from_recent_topics():
    '''
    Removes the last entered item of the recently viewed list
    '''
    del(session['recent'][-1])         


def before_request():
    '''
    Defines actions that are run before the every request
    '''
    session.permanent = True
    if not('settings' in session):
        session['settings'] = {
            'global_search_in_files': False, 'search_in_subfiles': True}
    if not('es_settings' in session):
        session['es_settings'] = {'update_markdown': False, 
            'update_pdf': False, 'update_audio': False, 
            'update_video': False, 'update_folder': False
            }
    if not('recent' in session):
        session['recent'] = []



def is_path_valid(path):
    '''
    Checks that a requested path is not outside the server range
    '''
    abs_path = os.path.abspath(path)
    abs_path = os.path.normpath(abs_path)
    base_normalize_path = os.path.normpath(base_path)
    if dir_breaks == '\\':
        base_normalize_path = base_normalize_path.replace(
            dir_breaks, dir_breaks+dir_breaks)
    if re.search(r'^'+base_normalize_path, abs_path) == None:
        return False
    else:
        return True

def get_local_file(file_and_path):
    '''
    Provides local files for download
    '''
    return _get_os_file(file_and_path, embed=False) 

def get_embed_file(file_and_path):
    '''
    Provides local files to be embedded into html
    '''
    return _get_os_file(file_and_path, embed=True)   

def _get_os_file(file_and_path, embed):
    '''
    Provides local files to be embedded into html, or downloaded
    '''
    separated = file_and_path.split('/')
    path = base_path + dir_breaks + dir_breaks.join(separated[:-1])
    filename = separated[-1]
    if is_path_valid(path):
        if embed == True:
            return send_from_directory(path, filename, as_attachment=False)
        else:
            return send_from_directory(path, filename, as_attachment=True)    
    else:
        return abort(404) 


def search_requested(f):
    '''
    Tries to return search results if a search term was given
    '''
    @wraps(f)
    def search_locally(*args, **kwargs):
        if 'search' in request.args:
            searchterm = request.args['search']
            if file_group in request.args:
                search_type = file_group
                search_path = request.args[file_group]
            elif folder_group in request.args:
                search_type = folder_group
                search_path = request.args[folder_group]
            else:
                search_type = ''
                search_path = root_web_path

            search_results = get_search_result(searchterm, search_type, search_path)
            return render_template('search_result.html', header=header(), search_results=search_results, len=len)

        return f(*args, **kwargs)
    return search_locally


@search_requested
def home():
    '''
    Defaults to the mainpage
    '''
    t = topics()
    recent_topics = get_recent_topics()
    return render_template('index.html', base_topics=t.base_topics, sub_topics=t.sub_topics, \
        header=header(), len=len, recent_topics=recent_topics)


def get_subpage(subpath):
    '''
    Returns the requested topic saved in elastic, or None if it wasn't found
    '''
    try:
        s = Search(using=es_client).query('match', web_path=subpath)
        s = s.source(excludes=attachment_fields)
        res = s[0].execute()
        return None if (res.hits.total == 0) else res.hits[0]
    except (TransportError, NewConnectionError, ConnectionRefusedError):
        logging.critical('Can\'t connect to elastic from flask')
        sys.exit()


@search_requested
def sub_pages(subpath=None):
    '''
    Renders subtopics according to their type
    '''
    if subpath == None:
        return abort(404)

    subpath = root_web_path + subpath
    if subpath[-1] == '/':
        subpath = subpath[:-1]

    first_hit = get_subpage(subpath)
    norm_subpath = subpath.replace(root_web_path,'/')[1:]
    if first_hit == None:
        return abort(404)
    else:
        add_to_recent_topics(norm_subpath)
        if first_hit.meta.index == 'markdown':
            headings = json.loads(first_hit.saved_md.header_ids)
            return render_template('md_content.html', md_content=Markup(first_hit.saved_md.converted_html),
                                   header=header(), headings=headings, curr_topic=first_hit.name)
        elif first_hit.meta.index == 'pdf':
            pdf_src = url_for('get_embed_file', file_and_path=norm_subpath)
            return render_template('pdf_content.html', pdf_src=pdf_src)
        elif first_hit.meta.index == 'audio':
            return render_template('audio.html', file_and_path=norm_subpath, type=first_hit.mimetype, header=header())
        elif first_hit.meta.index == 'video':
            return render_template('video.html', file_and_path=norm_subpath, type=first_hit.mimetype, header=header())
        elif first_hit.meta.index == folder_group:
            remove_from_recent_topics()
            sub_t = topics(first_hit.web_path)
            return render_template("subsection.html", base_topics=sub_t.base_topics, sub_topics=sub_t.sub_topics,
                                section=norm_subpath, header=header(), len=len)
        else:
            remove_from_recent_topics()
            return abort(404)


@search_requested
def settings():
    '''
    Page to define search settings 
    '''
    if request.method == 'POST':
        if 'btnSearchSettings' in request.form:
            update_search_settings(request.form)
        if 'btnEsUpdate' in request.form:
            es_update_requested(request.form)

    s = SearchSettings(
        session['settings']['global_search_in_files'], session['settings']['search_in_subfiles'])
    
    es_settings = ElasticSettings(session['es_settings']['update_markdown'], 
        session['es_settings']['update_pdf'], session['es_settings']['update_audio'], 
        session['es_settings']['update_video'], session['es_settings']['update_folder'])
    
    return render_template('settings.html', header=header(), search_sets=s, es_sets=es_settings)


def update_search_settings(form_data):
    '''
    Updates search settings for the current session
    '''
    session['settings']['global_search_in_files'] = ('globalSearchInFiles' in form_data)
    session['settings']['search_in_subfiles'] = ('searchInSubFiles' in form_data)


def es_update_requested(form_data):
    '''
    Updates elastic settings for the current session.
    If at least one index was selected, an update to elastic is triggered
    '''
    es_update = []
    session['es_settings']['update_markdown'] = ('updateMarkdown' in form_data)
    session['es_settings']['update_pdf'] = ('updatePdf' in form_data)
    session['es_settings']['update_audio'] = ('updateAudio' in form_data)
    session['es_settings']['update_video'] = ('updateVideo' in form_data)
    session['es_settings']['update_folder'] = ('updateFolder' in form_data)
    if session['es_settings']['update_markdown']:
        es_update.append('markdown')
    if session['es_settings']['update_pdf']:
        es_update.append('pdf')
    if session['es_settings']['update_audio']:
        es_update.append('audio')
    if session['es_settings']['update_video']:
        es_update.append('video')
    if session['es_settings']['update_folder']:
        es_update.append('folder')
    
    if len(es_update):
        update_elastic(es_update)


def update_elastic(update_indices):
    '''
    Updates elastic for checked indices
    '''
    es_sync_scheduler.add_job(
        sync_elastic, id='update_es', kwargs=
        {'app': current_app._get_current_object(), 
        'update_indices': update_indices}
        )
    if not(es_sync_scheduler.running):
        es_sync_scheduler.start()


