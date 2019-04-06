from .models import audio, video, pdf, folder, markdown
from elasticsearch_dsl.connections import connections
from elasticsearch.exceptions import TransportError
from urllib3.exceptions import NewConnectionError
from elasticsearch.client.cat import CatClient
from src.config.config import es_host, es_port
import sys
import asyncio 

used_es_indices = ['markdown', 'pdf', 'audio', 'video', 'folder']

class ElasticSettings:
    '''
    Settings for elastic that can be used on the website
    '''
    def __init__(self, update_markdown, update_pdf, update_audio, update_video, update_folder):
        self.update_markdown = update_markdown
        self.update_pdf = update_pdf
        self.update_audio = update_audio
        self.update_video = update_video
        self.update_folder = update_folder


def setup_elastic():
    '''
    Creates a connection to elastic and initialises all needed documents
    '''
    es_connect_timeout = 0
    connected_to_es = False
    while (connected_to_es == False):
        try:
            es_client = connections.create_connection(host=es_host, port=es_port, timeout=60)
            es_act_indices = get_es_indices(es_client)
            connected_to_es = True
        except (TransportError, NewConnectionError, ConnectionRefusedError):
            es_connect_timeout += 1
            if es_connect_timeout < 60:
                print('Can\'t connect to elastic, retrying in 1 second')
                asyncio.run(asyncio.sleep(1))
            else:
                print('Failed to connect to elastic')
                sys.exit()

    _init_doc(folder.FolderDoc, es_act_indices)
    _init_doc(audio.AudioDoc, es_act_indices)
    _init_doc(video.VideoDoc, es_act_indices)
    _init_doc(pdf.PdfDoc, es_act_indices)
    _init_doc(markdown.MarkdownDoc, es_act_indices)

    return es_client


def _is_used_index(found_es_index):
    '''
    Returns True when the found index in es is used by this app
    '''
    if found_es_index in used_es_indices:
        return True
    else:
        return False

def get_es_indices(client):
    '''
    Returns a list of all found indices in elastic
    '''
    cat = CatClient(client)
    res = cat.indices(params={'h': 'index'})
    if not(res):
        return []
    found_indices = (i for i in res[:-1].split('\n') if _is_used_index(i))
    es_indices = [i for i in found_indices]
    return es_indices

def _init_doc(doc, es_indices):
    '''
    Only inits mapping if index isn't in elastic
    '''
    if not(doc.Index.name in es_indices):
        doc.init()

