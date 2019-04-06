from src.config.config import supp_mime_types

class web_file:
    '''
    Represents a file with additional elements to define how the file gets displayed inside a page
    '''
    def __init__(self, web_path, filename, filetype, file_icon, mimetype):
        self.path = web_path
        self.name = filename
        self.icon = file_icon
        self.type = filetype
        self.mimetype = mimetype
        self.get_emb_toggle(filetype)

    def get_emb_toggle(self, filetype):
        if filetype == 'audio':
            self.emb_toggle = 'fas fa-volume-up'
        elif filetype == 'video':
            self.emb_toggle = 'fas fa-video'
        else:
            self.emb_toggle = ''

   

