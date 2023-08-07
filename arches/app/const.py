from enum import Enum, unique

@unique
class IntegrityCheck(Enum):
    NODE_HAS_ONTOLOGY_GRAPH_DOES_NOT = 1005
    NODELESS_NODE_GROUP = 1012
