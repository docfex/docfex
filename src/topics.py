from elasticsearch_dsl import Search
from src.config.config import base_path, dir_breaks, supp_mime_types, root_web_path, folder_group, file_group
from .models.web_file import web_file
from .models.web_folder import web_folder
from src.elastic.models.attachments import attachment_fields
from src.elastic.setup import es_client
import os
import mimetypes

class topics:
    '''
    Filters a directory for folders and supported files providing them in dictionaries.
    Files are saved with their mimetype
    '''
    @staticmethod
    def get_root_topiclist():
        '''
        Returns a list of folders in the root path
        '''
        root_topics = []
        res = topics._find_topics(root_web_path)
        for hit in res:
            if hit.meta.doc_type == folder_group:
                folder = web_folder(hit.web_path, hit.name, hit.web_icon)
                root_topics.append(folder)
        return root_topics

    @staticmethod
    def _split_file_folder(hit, topic_dict):
        '''
        Moves a hit either in file or foldergroup
        '''
        if hit.meta.doc_type == folder_group:
            if not(folder_group in topic_dict):
                topic_dict[folder_group] = []
            folder = web_folder(hit.web_path, hit.name, hit.web_icon)
            topic_dict[folder_group].append(folder)
        elif hit.meta.doc_type == file_group:
            if not(file_group in topic_dict):
                topic_dict[file_group] = []

            wf = web_file(hit.web_path, hit.name, hit.meta.index, hit.web_icon, hit.mimetype)
            topic_dict[file_group].append(wf)

    @staticmethod
    def _find_topics(parent_path):
        '''
        Returns a list of topics that have the same parent
        '''
        s = Search(using=es_client).query('term', parent_path=parent_path)
        exclude_fields = attachment_fields[:]
        exclude_fields.append('saved_md')
        s = s.source(exclude=exclude_fields)
        s = s.sort(
            {"web_path": {"order": "asc"}}
        )
        cnt = s.count()
        return s[:cnt].execute()

    def __init__(self, topic_parent_path=root_web_path):
        self.topic_parent_path = topic_parent_path
        self.base_topics = {}
        self.get_base_topics()
        self.sub_topics = {}
        self.get_sub_topics()

    def get_base_topics(self):
        '''
        Gets folders and files from the current path
        '''
        res = topics._find_topics(self.topic_parent_path)
        for hit in res:
            topics._split_file_folder(hit, self.base_topics)

    def get_sub_topics(self):
        '''
        Gets folders and files from a subfolder of the current path
        '''
        if folder_group in self.base_topics:
            for folder in self.base_topics[folder_group]:
                res = topics._find_topics(folder.path)
                for hit in res:
                    if not(folder.name in self.sub_topics):
                        self.sub_topics[folder.name] = {}
                    
                    topics._split_file_folder(hit, self.sub_topics[folder.name])

