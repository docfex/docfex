from src.config.config import base_path, dir_breaks, root_web_path, file_upload_path
import re
import markdown


def set_header(base_html, filename):
    '''
    Sets the filename as header h1 for the file.
    Sets 'md_header' as id for this header element to be referenced by own styles
    '''
    base_html = '<h1 id="md_header">' + filename + '</h1><hr>'
    return base_html

def conv_md_to_html(md_file):
    '''
    Converts a file written in markdown to HTML5
    '''
    file_content = ''
    with open(md_file) as f:
        file_content = f.read()
    
    base_html = set_header('', md_file.split(dir_breaks)[-1])
    base_html = base_html + markdown.markdown(file_content, extensions=['codehilite','fenced_code'])
    return base_html    

def bootify_html_nav(base_html):
    '''
    Adds navigation to the converted markdown file.
    A navigation is created for each heading
    '''
    bootified_html = ''
    last_found = 0
    headings = []
    nav_header_offset = 4
    for m in re.finditer(r'<h\d([\w\W]*?)>([\w\W]*?)<\/h(\d)>', base_html):
        if re.search(r'md_header', m.group(1)):
            continue
        valid_id = ''.join(m.group(2).split())
        start_anchor = '<div class="anchor"><a id="' + valid_id + '">&nbsp;</a>'   
        bootified_html += base_html[last_found:m.start(0)] + start_anchor + base_html[m.start(0):m.end(0)] + '</div>'
        last_found = m.end(0)
        head_nr = int(m.group(3))
        if head_nr <= 6-nav_header_offset:
            headings.append((head_nr+nav_header_offset, valid_id, m.group(2)))
        else:
            headings.append((0, valid_id, m.group(2))) 
        
    bootified_html += base_html[last_found:]
    return bootified_html, headings

def bootify_html_quotes(base_html):
    '''
    Ads the 'blockquote' class to a blockqoute element for later styling
    '''
    bootified_html = ''
    last_found = 0
    for m in re.finditer(r'<blockquote[\w\W]*?()>', base_html):
        bootstrap_class = ' class="blockquote"'   
        bootified_html += base_html[last_found:m.start(1)] + bootstrap_class + base_html[m.start(1):m.end(0)]
        last_found = m.end(0)
        
    bootified_html += base_html[last_found:]
    return bootified_html

def link_images(base_html, filename):
    '''
    Corrects local image links in the markdown file
    '''
    bootified_html = ''
    last_found = 0
    filename = filename.replace(base_path + dir_breaks, '')
    filename = filename.replace(dir_breaks, '/')
    filename = '/'.join(filename.split('/')[:-1]).replace(dir_breaks, '/')
    for m in re.finditer(r'<img[\w\W]*?src=\"((?!(https=|ftp):)[\w\/.]+?)\"\s/>', base_html):
        web_filepath = filename + '/' + m.group(1)
        # url hardcoded since outside flask scope
        data_link = root_web_path + file_upload_path + '/' + web_filepath
        bootified_html += base_html[last_found:m.start(1)] + data_link + base_html[m.end(1):m.end(0)]
        last_found = m.end(0)
        
    bootified_html += base_html[last_found:]
    return bootified_html

def fluid_images(base_html):
    '''
    Makes images fluid using the 'img-fluid' class from Bootstrap 4
    '''
    bootified_html = ''
    last_found = 0
    for m in re.finditer(r'<img()[\w\W]*?/>', base_html):
        fluid_img = ' class="img-fluid"'
        bootified_html += base_html[last_found:m.start(1)] + fluid_img + base_html[m.end(1):m.end(0)]
        last_found = m.end(0)
    bootified_html += base_html[last_found:]
    return bootified_html    

def render_markdown(filename):
    '''
    Converts a markdown file into HTML5 with attributes to be used with Bootstrap 4
    Returns the converted html file and a list of header ids to be used as navigation
    '''
    conv_md = conv_md_to_html(filename)
    bootstraped_html, headings = bootify_html_nav(conv_md)
    bootstraped_html = bootify_html_quotes(bootstraped_html)
    bootstraped_html = link_images(bootstraped_html, filename)
    bootstraped_html = fluid_images(bootstraped_html)
    return bootstraped_html, headings


