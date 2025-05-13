from enum import Enum, unique


IntegrityCheckDescriptions = {
    1005: "Nodes with ontologies found in graphs without ontologies",
    1012: "Node Groups without contained nodes",
    1013: "Node Groups without a grouping node",
    1014: "Publication missing for language",
    1015: "Graphs missing slugs",
    1016: "Nodes with excess widget configurations",
    1017: "Nodes with missing widget configurations",
}


@unique
class IntegrityCheck(Enum):
    NODE_HAS_ONTOLOGY_GRAPH_DOES_NOT = 1005
    NODELESS_NODE_GROUP = 1012
    NODEGROUP_WITHOUT_GROUPING_NODE = 1013
    PUBLICATION_MISSING_FOR_LANGUAGE = 1014
    GRAPH_MISSING_SLUG = 1015
    TOO_MANY_WIDGET_CONFIGS = 1016
    # TOO_FEW_WIDGET_CONFIGS isn't currently a failure condition,
    # but it might be in the future.
    TOO_FEW_WIDGET_CONFIGS = 1017

    def __str__(self):
        return IntegrityCheckDescriptions[self.value]


class ExtensionType(Enum):
    DATATYPES = "datatypes"
    ETL_MODULES = "etl_modules"
    FUNCTIONS = "functions"
    SEARCH_COMPONENTS = "search_components"
    PERMISSIONS_FRAMEWORKS = "permissions"
