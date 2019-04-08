from src.config.config import cloud_storage_url, repo_url, notes_url, root_web_path
from .topics import topics

class header:
    '''
    Gets all needed values that are displayed in the header section of the page
    '''
    def __init__(self):
        self.header_topics = topics.get_root_topiclist()
        self.cloud_storage_url = cloud_storage_url
        self.repo_url = repo_url
        self.notes_url = notes_url
        self.root_web_path = root_web_path


