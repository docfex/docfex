from .web_file import web_file

class web_content(web_file):
    '''
    Represents a preview of found search term inside a file 
    '''
    def __init__(self, preview='', ** kwargs):
        super(web_content, self).__init__(** kwargs)
        # offset disabled until elastic returns match offsets
        #self.rel_offset = rel_offset
        self.preview = preview


