from elasticsearch_dsl import Index, MetaField
from .base import EsBase, BaseDoc, index_settings
from src.config.config import web_icons


class VideoSettings:
    _index = 'video'
    _type = 'file'

class VideoDoc(BaseDoc):
    '''
    Document class to represent a video file
    '''
    class Meta:
        dynamic = MetaField('strict')
        doc_type = VideoSettings._type

    class Index:
        name = VideoSettings._index
        doc_type = VideoSettings._type
        settings = index_settings


class EsVideo(EsBase):
    '''
    Elastic model for a Video file
    '''
    class VideoObj(EsBase.BaseObj):
        '''
        Object holding values to be stored using VideoDoc
        '''
        web_icon = ''
        def __init__(self, web_icon=web_icons['video'], ** kwargs):
            self.web_icon = web_icon
            super(EsVideo.VideoObj, self).__init__(web_icon=self.web_icon, ** kwargs)


    def __init__(self, es_id='', ** kwargs):
        self._own_doc = None
        self._own_index = VideoSettings._index
        self._own_type = VideoSettings._type
        self._own_obj = self.VideoObj(** kwargs)
        super(EsVideo, self).__init__(es_id)   

    @property
    def own_obj(self):
        '''
        Video object of the current instance
        '''
        return self._own_obj

    @property
    def own_doc(self):
        '''
        Video document of the current instance
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
        Saves a video document with the video object values of this instance
        '''
        self._own_doc = VideoDoc(meta={'id': self.es_id}, name=self._own_obj.name, 
            web_path=self._own_obj.web_path, web_icon=self._own_obj.web_icon, 
            parent_path=self._own_obj.parent_path, last_modified=self._own_obj.last_modified, 
            os_size=self._own_obj.os_size, mimetype=self._own_obj.mimetype)
        return self._own_doc.save(** kwargs)

    def get(self, ** kwargs):
        '''
        Returns the video document of this instance
        '''
        self._own_doc = VideoDoc.get(id=self.es_id, ** kwargs)
        return self._own_doc
        
      
