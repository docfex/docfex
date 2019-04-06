from elasticsearch_dsl import Index, MetaField
from .attachments import AttachmentDoc, AttachmentEncDoc, ingest_attachment, attachment_fields
from .base import index_settings, EsBase, BaseDoc
from src.config.config import web_icons
import base64


class PdfSettings:
    _index = 'pdf'
    _type = 'file'

class PdfDoc(BaseDoc, AttachmentDoc):
    '''
    Document class to represent a pdf file
    '''
    class Meta:
        doc_type = PdfSettings._type

    class Index:
        name = PdfSettings._index
        doc_type = PdfSettings._type
        settings = index_settings


class EsPdf(EsBase):
    '''
    Elastic model for a pdf file
    '''
    class PdfObj(EsBase.BaseObj):
        '''
        Object holding values to be stored using PdfDoc
        '''
        web_icon = ''
        full_filename = ''
        def __init__(self, full_filename='', web_icon=web_icons['pdf'], ** kwargs):
            self.full_filename = full_filename
            self.web_icon = web_icon
            super(EsPdf.PdfObj, self).__init__(web_icon=self.web_icon, ** kwargs)


    def __init__(self, es_id='', full_filename='', ** kwargs):
        self._own_doc = None
        self._own_index = PdfSettings._index
        self._own_type = PdfSettings._type
        self._own_obj = self.PdfObj(full_filename, ** kwargs)
        super(EsPdf, self).__init__(es_id)   

    @property
    def own_obj(self):
        '''
        Pdf object of the current instance
        '''
        return self._own_obj

    @property
    def own_doc(self):
        '''
        Pdf document of the current instance
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
        Saves a pdf document with the pdf object values of this instance
        '''
        pipe = self.es_id
        ingest_attachment(PdfDoc._get_connection(), pipe)
        with open(self._own_obj.full_filename, 'rb') as f:
            content = f.read()
        enc_doc = AttachmentEncDoc(id=self.es_id, enc_attachment=base64.b64encode(content).decode('ascii'))
        self._own_doc = PdfDoc(meta={'id': self.es_id}, name=self._own_obj.name,
            web_path=self._own_obj.web_path, web_icon=self._own_obj.web_icon,
            parent_path=self._own_obj.parent_path, encoded_obj=enc_doc,
            last_modified=self._own_obj.last_modified, os_size=self._own_obj.os_size,
            mimetype=self._own_obj.mimetype)
        return self._own_doc.save(pipeline=pipe, ** kwargs)

    def get(self, _source_exclude=[], ** kwargs):
        '''
        Returns the pdf document of this instance
        '''
        _exclude = []
        _exclude = _source_exclude[:] + attachment_fields[:]
        self._own_doc = PdfDoc.get(id=self.es_id, _source_exclude=_exclude, ** kwargs)
        return self._own_doc 


