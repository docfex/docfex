from elasticsearch_dsl import Index, MetaField
from .base import EsBase, BaseDoc, index_settings
from src.config.config import web_icons


class AudioSettings:
    _index = 'audio'
    _type = 'file'

class AudioDoc(BaseDoc):
    '''
    Document class to represent a audio file
    '''
    class Meta:
        dynamic = MetaField('strict')

    class Index:
        name = AudioSettings._index
        settings = index_settings

class EsAudio(EsBase):
    '''
    Elastic model for a audio file
    '''
    class AudioObj(EsBase.BaseObj):
        '''
        Object holding values to be stored using AudioDoc
        '''
        web_icon = ''
        def __init__(self, web_icon=web_icons['audio'], ** kwargs):
            self.web_icon = web_icon
            super(EsAudio.AudioObj, self).__init__(web_icon=self.web_icon, ** kwargs)

    def __init__(self, es_id='', ** kwargs):
        self._own_doc = None
        self._own_index = AudioSettings._index
        self._own_type = AudioSettings._type
        self._own_obj = self.AudioObj(** kwargs)
        super(EsAudio, self).__init__(es_id)   

    @property
    def own_obj(self):
        '''
        Audio object of the current instance
        '''
        return self._own_obj

    @property
    def own_doc(self):
        '''
        Audio document of the current instance
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
        Saves a audio document with the audio object values of this instance
        '''
        self._own_doc = AudioDoc(meta={'id': self.es_id}, name=self._own_obj.name,
            web_path=self._own_obj.web_path, web_icon=self._own_obj.web_icon,
            parent_path=self._own_obj.parent_path, last_modified=self._own_obj.last_modified,
            os_size=self._own_obj.os_size, mimetype=self._own_obj.mimetype)

        return self._own_doc.save(** kwargs) 

    def get(self, ** kwargs):
        '''
        Returns the audio document of this instance
        '''
        self._own_doc = AudioDoc.get(id=self.es_id, ** kwargs)         
        return self._own_doc
        
      
