from elasticsearch_dsl import Document, Index, analyzer, tokenizer, Search
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl.field import Keyword, Text, Date, Long
from uuid import uuid5, NAMESPACE_URL
import abc


name_analyzer = analyzer('name_analyzer', 
    tokenizer=tokenizer('trigram', 'nGram', min_gram=3, max_gram=20),
    filter=['lowercase']
)

index_settings = {
    'number_of_shards': 2,
    'sort.field': 'web_path',
    'sort.order': 'desc',
    'codec': 'best_compression',
    'max_ngram_diff': 20
}

class BaseDoc(Document):
    '''
    Document including fields neccessary for all items
    '''
    name = Text(boost=2, analyzer=name_analyzer)
    mimetype = Keyword(index=False)
    web_path = Keyword()
    web_icon = Keyword(index=False)
    parent_path = Keyword()
    last_modified = Date(index=False)
    os_size = Long(index=False)

class EsBase:
    '''
    Base class of every elastic item
    '''
    __metaclass__ = abc.ABCMeta
    es_id = ''

    class BaseObj(object):
        '''
        Object holding values to be stored using BaseDoc
        '''
        name = ''
        mimetype = ''
        web_path = ''
        web_icon = ''
        parent_path = ''
        os_size = 0
        last_modified = ''

        def __init__(self, web_path, os_size=0, last_modified='', name='', web_icon='', parent_path='', mimetype=''):
            '''
            web_path must be provided since it is used to get the unique es_id
            '''
            self.os_size = os_size
            self.name = name
            self.web_path = web_path
            self.web_icon = web_icon
            self.mimetype = mimetype
            self.parent_path = parent_path
            self.last_modified = last_modified


    def __init__(self, es_id=''):
        if not(es_id):
            self.es_id = self.get_es_id()   

    @property
    @abc.abstractmethod
    def own_obj(self):
        '''
        Provides the object of the current elastic model
        Given object must inherit from BaseObj
        '''

    @property
    @abc.abstractmethod
    def own_doc(self):
        '''
        Document of this instance
        '''

    @property
    @abc.abstractmethod
    def own_index(self):
        '''
        Index of this document instance
        '''

    @property
    @abc.abstractmethod
    def own_type(self):
        '''
        Type of this document instance
        '''       

    def get_es_id(self):
        self.es_id = str(uuid5(NAMESPACE_URL, self.own_obj.web_path)) 
        return self.es_id   

    @abc.abstractmethod
    def save(self, ** kwargs):
        '''
        Saves the document representing this class
        '''

    @abc.abstractmethod
    def get(self, ** kwargs):
        '''
        Gets the document representing this class
        '''

    def delete(self, ** kwargs):
        '''
        Function to delete the document holding the object of this class.
        Deletes document using the web_path
        '''
        if self.own_doc == None:
            return
        s = Search(using=self.own_doc._get_connection())
        s = s.query('term', web_path=self.own_obj.web_path)
        s.delete()

    def exists(self, ** kwargs):
        i = Index(name=self.own_index)
        if not(i.exists()):
            return False
        try:
            self.get(_source_excludes=['*'])
            return True
        except NotFoundError:
            return False
