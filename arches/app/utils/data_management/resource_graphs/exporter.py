# from arches.app.models.models import VwExportNodes as Node
# from arches.app.models.models import VwExportEdges as Edges
import csv
from pprint import pprint as pp
import os
from arches.app.models.graph import Graph
from arches.app.models.models import CardXNodeXWidget, Form, FormXCard, Report
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

def export(export_dir):
    """
    Exports existing graphs as Gephi nodes and edges files to a directory
    """
    write_nodes(export_dir)
    write_edges(export_dir)

def write_nodes(export_dir):
    nodes = Node.objects.all()
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
    edges = Edge.objects.all()
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

def get_card_x_node_x_widget_data_for_export(resource_graph):
    cards_x_nodes_x_widgets = []
    for card in  resource_graph['cards']:
        cards_x_nodes_x_widgets = CardXNodeXWidget.objects.filter(card=card['cardid'])
    return cards_x_nodes_x_widgets

def get_forms_for_export(resource_graph):
    forms = Form.objects.filter(graph_id=resource_graph['graphid'])
    return forms

def get_form_x_card_data_for_export(resource_graph):
    forms_x_cards = []
    for form in resource_graph['forms']:
        forms_x_cards = forms_x_cards + list(FormXCard.objects.filter(form_id=form.formid))
    return forms_x_cards

def get_report_data_for_export(resource_graph):
    reports = []
    reports = Report.objects.filter(graph_id=resource_graph['graphid'])
    return reports

def get_graphs_for_export(graphids=None):
    graphs = {}
    graphs['graph'] = []
    if graphids == None or graphids[0] == 'all':
        resource_graph_query = JSONSerializer().serializeToPython(Graph.objects.all().exclude(name='Arches configuration'))
    elif graphids[0] == 'resources':
        resource_graph_query = JSONSerializer().serializeToPython(Graph.objects.filter(isresource=True).exclude(name='Arches configuration'))
    elif graphids[0] == 'branches':
        resource_graph_query = JSONSerializer().serializeToPython(Graph.objects.filter(isresource=False).exclude(name='Arches configuration'))
    else:
        resource_graph_query = JSONSerializer().serializeToPython(Graph.objects.filter(graphid__in=graphids))

    for resource_graph in resource_graph_query:
        resource_graph['cards_x_nodes_x_widgets'] = get_card_x_node_x_widget_data_for_export(resource_graph)
        resource_graph['forms'] = get_forms_for_export(resource_graph)
        resource_graph['forms_x_cards'] = get_form_x_card_data_for_export(resource_graph)
        resource_graph['reports'] = get_report_data_for_export(resource_graph)
        graphs['graph'].append(resource_graph)
    return graphs
