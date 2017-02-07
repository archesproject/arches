class BaseDataType(object):

    def __init__(self, model=None):
        self.datatype_model = model

    def append_to_document(self, document, nodetype):
        print 'passing'
