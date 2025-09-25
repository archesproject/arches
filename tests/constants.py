from enum import Enum
from uuid import UUID

"""
Constants for use only in Arches test suite.
Enumerations are grouped by test graph & should include things like:
    graphid, nodeids, nodegroupids, and resourceids
"""


class AllDatatypesTestGraph(Enum):
    GRAPH_ID = UUID("d71a8f56-987f-4fd1-87b5-538378740f15")
    BOOLEAN_NODE_NODEGROUP = UUID("fa6614e4-c8c0-11ed-a172-0242ac130009")
    BOOLEAN_SWITCH_NODE = UUID("088e7d2c-c8c1-11ed-a172-0242ac130009")
    RESOURCE1 = UUID("44000000-0000-0000-0000-000000000000")


class CardinalityTestGraph(Enum):
    GRAPH_ID = UUID("2f7f8e40-adbc-11e6-ac7f-14109fd34195")
    RESOURCE1 = UUID("40000000-0000-0000-0000-000000000000")
