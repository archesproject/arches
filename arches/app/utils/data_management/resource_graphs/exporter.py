from arches.app.models.models import VwExportNodes as Nodes
from arches.app.models.models import VwExportEdges as Edges
import csv
from pprint import pprint as pp
import os

def export(export_dir):
    """
    Exports existing graphs as Gephi nodes and edges files to a directory
    """
    write_nodes(export_dir)
    write_edges(export_dir)

def write_nodes(export_dir):
    nodes = Nodes.objects.all()
    entitytypeids = {}
    for node in nodes:
        if node.assettype not in entitytypeids:
            entitytypeids[node.assettype] = []
        entitytypeids[node.assettype].append([node.id,node.label,node.mergenode,node.businesstablename])

    for k, v in entitytypeids.iteritems():
        with open(os.path.join(export_dir, k + '_nodes.csv'), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter= ',')
            writer.writerow(['Id','Label','mergenode','businesstablename'])
            writer.writerow([k+':'+k,k,k,''])
            for node in v:
                writer.writerow(node)

def write_edges(export_dir):
    edges = Edges.objects.all()
    entitytypeids = {}
    for edge in edges:
        if edge.assettype not in entitytypeids:
            entitytypeids[edge.assettype] = []
        entitytypeids[edge.assettype].append([edge.source,edge.target,"Directed",edge.target,edge.label,1.0])

    for k, v in entitytypeids.iteritems():
        with open(os.path.join(export_dir, k + '_edges.csv'), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter= ',')
            writer.writerow(['Source','Target','Type','Id','Label','Weight'])
            for node in v:
                writer.writerow(node)