from src.config.config import preview_len, file_group, folder_group, max_found_names, max_found_content
from src.elastic.models.attachments import attachment_fields
from .elastic.setup import get_es_indices, es_client
from flask import Markup, session
from .models.web_file import web_file
from .models.web_folder import web_folder
from .models.web_content import web_content
from elasticsearch_dsl import Search, Q
import re


class SearchSettings:
    '''
    Defines search settings available for the website
    '''
    def __init__(self, global_search_in_files=False, search_in_subfiles=True):
        self.global_search_in_files = global_search_in_files
        self.search_in_subfiles = search_in_subfiles


def get_search_result(searchterm, search_type, search_path):
    '''
    Returns a list of hits from elastic that matched the searchterm
    '''
    if search_type == file_group:
        filter_q = Q('match', web_path=search_path)
    elif search_type == folder_group:
        filter_q = Q('wildcard', web_path=search_path + '*')
    else:
        filter_q = None

    found_terms = {}
    exclude_fields = attachment_fields[:]
    exclude_fields.append('saved_md')
    _search_file_foldername(searchterm, found_terms, filter_q, exclude_fields)
    if (session['settings']['global_search_in_files']) or (search_type == file_group) \
            or ((search_type == folder_group) and (session['settings']['search_in_subfiles'])):
        
        _search_in_files(searchterm, found_terms, filter_q, exclude_fields)
    
    return found_terms


def _search_file_foldername(searchterm, found_terms, filter_query, exclude_fields):
    '''
    Searches only for file/foldernames that match the searchterm
    '''
    searchterm = searchterm.lower()
    q = Q('match', name=searchterm) | Q('query_string', default_field='name', query=searchterm)
    s = Search(using=es_client).query(q).sort('_score')
    s = s.source(exclude=exclude_fields)
    if filter_query != None:
        s = s.filter(filter_query)
    res = s[0:max_found_names].execute()
    for hit in res:
        if hit.meta.doc_type == folder_group:
            if not (folder_group in found_terms):
                found_terms[folder_group] = []
            folder = web_folder(hit.web_path, hit.name, hit.web_icon)
            found_terms[folder_group].append(folder)
        elif hit.meta.doc_type == file_group:
            if not (file_group in found_terms):
                found_terms[file_group] = []
            wf = web_file(hit.web_path, hit.name, hit.meta.index,
                          hit.web_icon, hit.mimetype)
            found_terms[file_group].append(wf)


def _search_in_files(searchterm, found_terms, filter_query, exclude_fields):
    '''
    Searches the searchterm inside supported text files
    '''
    es_indices = get_es_indices()
    search_indices = []
    if 'pdf' in es_indices:
        search_indices.append('pdf')
    if 'markdown' in es_indices:
        search_indices.append('markdown')
    if len(search_indices) == 0:
        return    

    q = Q('query_string', default_field='stored_attachment.content', query=searchterm)
    s = Search(using=es_client, index=search_indices).query(q).sort('_score')
    s = s.source(exclude=exclude_fields)
    s = s.highlight_options(pre_tags='<em class="hl-found">', post_tags='</em>')
    s = s.highlight('stored_attachment.content', fragment_size=preview_len)
    if filter_query != None:
        s = s.filter(filter_query)
    res = s[0:max_found_content].execute()
    for hit in res:
        for fragment in hit.meta.highlight['stored_attachment.content']:
            if not ('content' in found_terms):
                found_terms['content'] = []
            preview = ''
            last_end = 0
            for m in re.finditer(r'(<em class="hl-found">)([\s\S]*?)(<\/em>)', fragment):
                preview += fragment[last_end:m.start()] + Markup(m.group(1)) + \
                    m.group(2) + Markup(m.group(3))
                last_end = m.end()
            preview += fragment[last_end:]
            content = web_content(preview, web_path=hit.web_path, filename=hit.name,
                filetype=hit.meta.index, file_icon=hit.web_icon, mimetype=hit.mimetype)
            found_terms['content'].append(content)

