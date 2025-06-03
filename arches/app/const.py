from enum import Enum, unique
from uuid import UUID


IntegrityCheckDescriptions = {
    1005: "Nodes with ontologies found in graphs without ontologies",
    1012: "Node Groups without contained nodes",
    1013: "Node Groups without a grouping node",
    1014: "Publication missing for language",
    1015: "Graphs missing slugs",
    1016: "Nodes with excess widgets",
    1017: "Nodes missing widgets",
}


@unique
class IntegrityCheck(Enum):
    NODE_HAS_ONTOLOGY_GRAPH_DOES_NOT = 1005
    NODELESS_NODE_GROUP = 1012
    NODEGROUP_WITHOUT_GROUPING_NODE = 1013
    PUBLICATION_MISSING_FOR_LANGUAGE = 1014
    GRAPH_MISSING_SLUG = 1015
    TOO_MANY_WIDGETS = 1016
    # NO_WIDGETS isn't currently an error condition,
    # but it might be in the future.
    NO_WIDGETS = 1017

    def __str__(self):
        return IntegrityCheckDescriptions[self.value]


class ExtensionType(Enum):
    DATATYPES = "datatypes"
    ETL_MODULES = "etl_modules"
    FUNCTIONS = "functions"
    SEARCH_COMPONENTS = "search_components"
    PERMISSIONS_FRAMEWORKS = "permissions"


@unique
class DefaultLifecycleStates(Enum):
    PERPETUAL = UUID("4e2a6b8e-2489-4377-9c9f-29cfbd3e76c8")
    STANDARD = UUID("7e3cce56-fbfb-4a4b-8e83-59b9f9e7cb75")
    DRAFT = UUID("9375c9a7-dad2-4f14-a5c1-d7e329fdde4f")
    ACTIVE = UUID("f75bb034-36e3-4ab4-8167-f520cf0b4c58")
    RETIRED = UUID("d95d9c0e-0e2c-4450-93a3-d788b91abcc8")
