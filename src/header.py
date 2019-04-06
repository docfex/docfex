from src.config.config import cloud_storage_url, repo_url, notes_url
from .topics import topics

class header:
    '''
    Gets all needed values that are displayed in the header section of the page
    '''
    def __init__(self, es_client):
        self.header_topics = topics.get_root_topiclist(es_client)
        self.cloud_storage_url = cloud_storage_url
        self.repo_url = repo_url
        self.notes_url = notes_url


