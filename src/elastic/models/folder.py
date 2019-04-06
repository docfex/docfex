from elasticsearch_dsl import Index, MetaField
from .base import EsBase, BaseDoc, index_settings
from src.config.config import web_icons

class FolderSettings:
    _index = 'folder'
    _type = 'folder'

class FolderDoc(BaseDoc):
    '''
    Document class to represent a folder
    '''
    class Meta:
        dynamic = MetaField('strict')
        doc_type = FolderSettings._type

    class Index:
        name = FolderSettings._index
        doc_type = FolderSettings._type
        settings = index_settings


class EsFolder(EsBase):
    '''
    Elastic model for a folder
    '''
    class FolderObj(EsBase.BaseObj):
        '''
        Object holding values to be stored using FolderDoc
        '''
        web_icon = ''
        def __init__(self, web_icon=web_icons['folder'], ** kwargs):
            self.web_icon = web_icon
            super(EsFolder.FolderObj, self).__init__(web_icon=self.web_icon, ** kwargs)

    def __init__(self, es_id='', ** kwargs):
        self._own_doc = None
        self._own_index = FolderSettings._index
        self._own_type = FolderSettings._type
        self._own_obj = self.FolderObj(** kwargs)
        super(EsFolder, self).__init__(es_id)   

    @property
    def own_obj(self):
        '''
        Folder object of the current instance
        '''
        return self._own_obj

    @property
    def own_doc(self):
        '''
        Folder document of the current instance
        None if document wasn't created or retrieved from elastic
        '''
        return self._own_doc

    @property
    def own_index(self):
        '''
        Index of this document instance
        '''
        return self._own_index

    @property
    def own_type(self):
        '''
        Type of this document instance
        '''
        return self._own_type

    def save(self, ** kwargs):
        '''
        Saves a folder document with the folder object values of this instance
        '''
        self._own_doc = FolderDoc(meta={'id': self.es_id}, name=self._own_obj.name,
            web_path=self._own_obj.web_path, web_icon=self._own_obj.web_icon,
            parent_path=self._own_obj.parent_path, last_modified=self._own_obj.last_modified,
            os_size=self._own_obj.os_size, mimetype=self._own_obj.mimetype)
        return self._own_doc.save(** kwargs)

    def get(self, ** kwargs):
        '''
        Returns the folder document of this instance
        '''
        self._own_doc = FolderDoc.get(id=self.es_id, ** kwargs)
        return self._own_doc
        
      
