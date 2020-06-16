class MultipleNodesFoundException(Exception):
    def __init__(self, name, nodes):
        self.nodes = nodes
        self.message = "Multiple nodes with the name '%s' were found" % name


class InvalidNodeNameException(Exception):
    def __init__(self, name):
        self.message = "Node with the name '%s' doesn't exist" % name
