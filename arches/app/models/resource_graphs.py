'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import uuid
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.db.models import F

class ResourceGraph(object):
    """
    Used for mapping complete resource graph objects to and from the database

    """

    def __init__(self, *args, **kwargs):
        self.root = None
        self.nodes = []
        self.edges = []
        self.nodegroups = []
        if args:
            if isinstance(args[0], basestring):
                try:
                    uuid.UUID(args[0])
                    root = models.Node.objects.get(pk=args[0])
                    self.get_nodes_and_edges(root)
                except(ValueError):
                    pass
                    #self.load(JSONDeserializer().deserialize(args[0]))
            elif isinstance(args[0], models.Node):
                self.get_nodes_and_edges(args[0])
            elif args[0]["nodes"] and args[0]["edges"]:
                self.nodes = args[0]["nodes"]
                self.edges = args[0]["edges"]

    def _save(self):
        """
        Saves an entity back to the db, returns a DB model instance, not an instance of self

        """
        collectorlist = []
        for i, node in enumerate(self.nodes):
            newNode = models.Node()

            try:
                uuid.UUID(str(node['nodeid']))
                newNode.nodeid = node['nodeid']
            except(ValueError):
                node['nodeid'] = str(uuid.uuid4())


            newNode.nodeid = node.get('nodeid')
            newNode.name = node.get('name', '')
            newNode.description = node.get('description','')
            newNode.istopnode = node.get('istopnode','')
            newNode.crmclass = node.get('crmclass','')
            newNode.datatype = node.get('datatype','')
            newNode.status = node.get('status','')
            newNode.nodegroup = self.insert_node_group(node)

            node['nodeid'] = newNode.nodeid
            newNode.save()

            self.nodes[i] = newNode


        for i, edge in enumerate(self.edges):
            newEdge = models.Edge()
            # self.get_node_id_from_text()

            try:
                uuid.UUID(edge['edgeid'])
            except(ValueError):
                edge['edgeid'] = str(uuid.uuid4())

            newEdge.edgeid = edge.get('edgeid')
            newEdge.rangenode_id = edge.get('rangenodeid')
            newEdge.domainnode_id = edge.get('domainnodeid')
            newEdge.ontologyproperty = edge.get('ontologyproperty', '')
            newEdge.branchmetadataid = edge.get('branchmetadataid', '')

            edge['edgeid'] = newEdge.edgeid
            newEdge.save()

            self.edges[i] = newEdge

        self.populate_null_nodegroupids()

        collectorlist = filter(lambda n: (n.nodeid==n.nodegroup_id) and (n.istopnode != False), self.nodes)
        for collector in collectorlist:
            edge = models.Edge.objects.get(rangenode = collector)
            collector.nodegroup.parentnodegroup = edge.domainnode.nodegroup
            collector.nodegroup.save()

    def populate_null_nodegroupids(self):
        noncollector_nodes = filter(lambda n: n.nodegroup == None, self.nodes)
        for node in noncollector_nodes:
            node.nodegroup = self.traverse_to_nodegroup(node)
            node.save()

    def traverse_to_nodegroup(self, node):
        range_edge = models.Edge.objects.get(rangenode = node)
        if range_edge.domainnode.nodegroup is not None:
            return range_edge.domainnode.nodegroup
        else:
            return self.traverse_to_nodegroup(range_edge.domainnode)

    def insert_node_group(self, node):
        if node.get('nodegroupid', '') != None:
            newNodeGroup = models.NodeGroup()
            newNodeGroup.cardinality = node.get('cardinality', '')
            newNodeGroup.nodegroupid = node.get('nodegroupid', '')
            newNodeGroup.save()
            return models.NodeGroup.objects.get(nodegroupid = newNodeGroup.nodegroupid)
        else:
            return None

    def get_nodes_and_edges(self, node):
        """
        Populate a ResourceGraph with the child nodes and edges of parameter: 'node'

        """

        self.root = node
        self.nodes.append(node)

        child_nodes, child_edges = node.get_child_nodes_and_edges()

        self.nodes.extend(child_nodes)
        self.edges.extend(child_edges)

        nodegroups = map(lambda n: n.nodegroup, filter(lambda n: n.is_collector(), self.nodes))

        self.nodegroups.extend(nodegroups)

    def append_branch(self, property, nodeid=None, branch_root=None, branchmetadataid=None):
        """
        Appends a branch onto this graph

        property: the property to use when appending the branch

        nodeid: if given will append the branch to this node, if not supplied will
        append the branch to the root of this graph

        branch_root: the root node of the branch you want to append

        branchmetadataid: get the branch to append based on the branchmetadataid,
        if given, branch_root takes precedence

        """

        if not branch_root:
            branch_root = models.Node.objects.get(branchmetadata=branchmetadataid, istopnode=True)
        branch_root.istopnode = False
        branch_graph = ResourceGraph(branch_root)
        new_branch = branch_graph.copy()
        newEdge = models.Edge(
            domainnode_id = (nodeid if nodeid else self.root.pk),
            rangenode = new_branch.root,
            ontologyproperty = property
        )
        newEdge.save()
        branch_graph.edges.append(newEdge)
        return branch_graph

    def copy(self):
        mapping = {}
        ret = ResourceGraph()
        self.root.pk = None
        self.root.save()
        mapping[self.root.pk] = self.root
        for edge in self.edges:
            if(edge.rangenode_id not in mapping):
                #mapping[edge.rangenode_id] = None
                edge.rangenode.pk = None
                mapping[edge.rangenode_id] = edge.rangenode.save()
            else:
                edge.rangenode = mapping[edge.rangenode_id]
            if(edge.domainnode_id not in mapping):
                edge.domainnode.pk = None
                mapping[edge.domainnode_id] = edge.domainnode.save()
            else:
                edge.domainnode = mapping[edge.domainnode_id]
            edge.pk = None
            edge.save()
            ret.edges.append(edge)
        for nodeid, node in mapping.iteritems():
            if str(self.root.pk) == str(nodeid):
                ret.root = node
            ret.nodes.append(node)

        return ret

    def get_node_id_from_text(self):
        for edge in self.edges:
            for node in self.nodes:
                if edge['domainnodeid'] == node['name']:
                    edge['domainnodeid'] = node['nodeid']
                if edge['rangenodeid'] == node['name']:
                    edge['rangenodeid'] = node['nodeid']
