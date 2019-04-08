from elasticsearch_dsl import Index, InnerDoc, MetaField
from elasticsearch_dsl.field import Text, Object
from elasticsearch import TransportError
from .attachments import AttachmentDoc, AttachmentEncDoc, ingest_attachment, attachment_fields
from .base import index_settings, EsBase, BaseDoc
from src.config.config import web_icons
from src.md_convert import render_markdown
import base64
import json


class MarkdownSettings:
    _index = 'markdown'
    _type = 'file'

class MarkdownStoredDoc(InnerDoc):
    converted_html = Text(index=False)
    header_ids = Text(index=False)

class MarkdownDoc(BaseDoc, AttachmentDoc):
    '''
    Document class to represent a markdown file
    Also stores the converted html version of the given markdown file
    '''
    saved_md = Object(MarkdownStoredDoc, enabled=False)

    class Meta:
        doc_type = MarkdownSettings._type

    class Index:
        name = MarkdownSettings._index
        doc_type = MarkdownSettings._type
        settings = index_settings


class EsMarkdown(EsBase):
    '''
    Elastic model for a markdown file
    '''
    class MarkdownObj(EsBase.BaseObj):
        '''
        Object holding values to be stored using MarkdownDoc
        '''
        web_icon = ''
        full_filename = ''
        def __init__(self, full_filename='', web_icon=web_icons['markdown'], ** kwargs):
            self.full_filename = full_filename
            self.web_icon = web_icon
            super(EsMarkdown.MarkdownObj, self).__init__(web_icon=self.web_icon, ** kwargs)


    def __init__(self, es_id='', full_filename='', **kwargs):
        self._own_doc = None
        self._own_index = MarkdownSettings._index
        self._own_type = MarkdownSettings._type
        self._own_obj = self.MarkdownObj(full_filename, **kwargs)
        super(EsMarkdown, self).__init__(es_id)   

    @property
    def own_obj(self):
        '''
        Markdown object of the current instance
        '''
        return self._own_obj

    @property
    def own_doc(self):
        '''
        Markdown document of the current instance
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
        Saves a markdown document with the markdown object values of this instance
        '''
        pipe = self.es_id
        ingest_attachment(MarkdownDoc._get_connection(), pipe)
        content, header_ids = render_markdown(self._own_obj.full_filename)
        inn_doc = MarkdownStoredDoc(id=self.es_id, converted_html=content, header_ids=json.dumps(header_ids))
        enc_doc = AttachmentEncDoc(id=self.es_id, enc_attachment=base64.b64encode(bytes(content,'utf-8')).decode('ascii'))
        self._own_doc = MarkdownDoc(meta={'id': self.es_id}, name=self._own_obj.name,
            web_path=self._own_obj.web_path, web_icon=self._own_obj.web_icon,
            parent_path=self._own_obj.parent_path, saved_md=inn_doc, encoded_obj=enc_doc,
            last_modified=self._own_obj.last_modified, os_size=self._own_obj.os_size,
            mimetype=self._own_obj.mimetype)
        
        # if markdown can't be read, index without content
        created = False
        try:
            created = self._own_doc.save(pipeline=pipe, ** kwargs)
        except TransportError:
            empty_enc_doc = AttachmentEncDoc(id=self.es_id, enc_attachment=base64.b64encode(b'indexing failed').decode('ascii'))
            self._own_doc.encoded_obj = empty_enc_doc
            created = self._own_doc.save()

        return created    

    def get(self, _source_exclude=[], ** kwargs):
        '''
        Returns the pdf document of this instance
        '''
        _exclude = []
        _exclude = _source_exclude[:] + attachment_fields[:]
        self._own_doc = MarkdownDoc.get(id=self.es_id, _source_exclude=_exclude, ** kwargs)
        return self._own_doc

