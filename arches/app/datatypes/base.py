class BaseDataType(object):

    def __init__(self, model=None):
        self.datatype_model = model

    def append_to_document(self, document, nodevalue):
        """
        Assigns a given node value to the corresponding key in a document in
        in preparation to index the document
        """
        pass

    def transform_import_values(self, value):
        """
        Transforms values from probably string/wkt representation to specified
        datatype in arches
        """
        return value

    def transform_export_values(self, value):
        """
        Transforms values from probably string/wkt representation to specified
        datatype in arches
        """
        return value

    def get_bounds(self, tile, node):
        """
        Gets the bounds of a geometry if the datatype is spatial
        """
        return None

    def get_layer_config(self, node=None):
        """
        Gets the layer config to generate a map layer (use if spatial)
        """
        return None

    def get_map_layer(self, node=None):
        """
        Gets the array of map layers to add to the map for a given node
        should be a dictionary including (as in map_layers table):
        nodeid, name, layerdefinitions, isoverlay, icon
        """
        return None

    def get_map_source(self, node=None):
        """
        Gets the map source definition to add to the map for a given node
        should be a dictionary including (as in map_sources table):
        name, source (json)
        """
        return None

    def get_pref_label(self, nodevalue):
        """
        Gets the prefLabel of a concept value
        """
        return None

    def get_display_value(self, tile, node):
        """
        Returns a list of concept values for a given node
        """
        return None

    def get_search_term(self, nodevalue):
        """
        Returns a nodevalue if it qualifies as a search term
        """
        return None

    def manage_files(self, previously_saved_tile, current_tile, request, node):
        """
        Updates files
        """
        pass
