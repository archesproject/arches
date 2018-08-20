define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/base-manager',
    'viewmodels/alert',
    'models/graph',
    'models/report',
    'views/graph/graph-manager/graph',
    'views/graph/graph-designer/graph-tree',
    'views/graph/graph-designer/node-form',
    'views/graph/graph-manager/branch-list',
    'views/graph/graph-designer/card-tree',
    'views/graph/permission-designer',
    'graph-designer-data',
    'arches',
    'viewmodels/graph-settings',
    'viewmodels/card',
    'view-data',
    'report-templates',
    'bindings/resizable-sidepanel',
    'datatype-config-components',
    'views/components/simple-switch'
], function($, _, ko, koMapping, BaseManagerView, AlertViewModel, GraphModel, ReportModel, GraphView, GraphTree, NodeFormView, BranchListView, CardTreeViewModel, PermissionDesigner, data, arches, GraphSettingsViewModel, CardViewModel, viewData, reportLookup) {
    var GraphDesignerView = BaseManagerView.extend({

        initialize: function(options) {
            var viewModel = options.viewModel;
            viewModel.graphid = ko.observable(data.graphid);
            viewModel.activeTab = ko.observable('graph');
            viewModel.viewState = ko.observable('design');
            viewModel.helpTemplate(viewData.help);
            viewModel.graphSettingsVisible = ko.observable(false);
            viewModel.graph = koMapping.fromJS(data['graph']);
            viewModel.ontologies = ko.observable(data['ontologies']);
            viewModel.ontologyClasses = ko.observable(data['ontologyClasses']);
            viewModel.cardComponents = data.cardComponents;

            var resources = ko.utils.arrayFilter(viewData.graphs, function(graph) {
                return graph.isresource;
            });
            var graphs = ko.utils.arrayFilter(viewData.graphs, function(graph) {
                return !graph.isresource;
            });

            viewModel.graph.ontology = ko.computed(function() {
                return viewModel.ontologies().find(function(obj) {
                    return obj.ontologyid === viewModel.graph.ontology_id();
                });
            });
            viewModel.groupedGraphs = ko.observable({
                groups: [
                    { name: 'Resource Models', items: resources },
                    { name: 'Branches', items: graphs }
                ]
            });

            viewModel.graphid.subscribe(function(graphid) {
                if (graphid && graphid !== '') {
                    viewModel.navigate(arches.urls.graph_designer(graphid));
                }
            });

            viewModel.graphModel = new GraphModel({
                data: data.graph,
                datatypes: data.datatypes,
                ontology_namespaces: data.ontology_namespaces
            });

            viewModel.datatypes = _.keys(viewModel.graphModel.get('datatypelookup'));

            viewModel.graphModel.on('changed', function(model, response) {
                if (viewModel.graphView) {
                    viewModel.graphView.redraw(true);
                }
                viewModel.alert(null);
                viewModel.loading(false);
                if (response.status !== 200) {
                    var errorMessageTitle = arches.requestFailed.title;
                    var errorMessageText = arches.requestFailed.text;
                    viewModel.alert(null);
                    if (response.responseJSON) {
                        errorMessageTitle = response.responseJSON.title;
                        errorMessageText = response.responseJSON.message;
                    }
                    viewModel.alert(new AlertViewModel('ep-alert-red', errorMessageTitle, errorMessageText));
                }
            });

            viewModel.graphModel.on('error', function(response) {
                viewModel.alert(new AlertViewModel('ep-alert-red', response.responseJSON.title, response.responseJSON.message));
            });

            viewModel.selectedNode = viewModel.graphModel.get('selectedNode');

            viewModel.saveNode = function(node) {
                if (node) {
                    viewModel.loading(true);
                    node.save(function(data) {
                        if (data.responseJSON.success === false || data.status === 500) {
                            viewModel.alert(new AlertViewModel('ep-alert-red', data.responseJSON.title, data.responseJSON.message));
                        }
                        else {
                            viewModel.cardTree.updateCards('update', viewModel.selectedNode().nodeGroupId(), data.responseJSON);
                            viewModel.permissionTree.updateCards('update', viewModel.selectedNode().nodeGroupId(), data.responseJSON);
                        }
                        viewModel.loading(false);
                    });
                }
            };

            viewModel.saveSelectedNode = function() {
                if (viewModel.selectedNode()) {
                    viewModel.saveNode(viewModel.selectedNode());
                }
            };

            viewModel.cardTree = new CardTreeViewModel({
                graph: viewModel.graph,
                graphModel: viewModel.graphModel
            });

            viewModel.permissionTree = new CardTreeViewModel({
                graph: viewModel.graph,
                graphModel: viewModel.graphModel,
                multiselect: true
            });

            viewModel.selectedCards = ko.computed(function() {
                var selection = viewModel.permissionTree.selection();
                if (selection) {
                    if (selection.widgets) {
                        return selection;
                    }
                    return selection.parent;
                } else {
                    return null;
                }
            });

            viewModel.selectedCard = ko.computed(function() {
                var selection = viewModel.cardTree.selection();
                if (selection) {
                    if (selection.widgets) {
                        return selection;
                    }
                    return selection.parent;
                } else {
                    return null;
                }
            });

            viewModel.nodeForm = new NodeFormView({
                graph: viewModel.graph,
                graphModel: viewModel.graphModel,
                loading: viewModel.loading,
                node: viewModel.selectedNode,
                restrictedNodegroups: data.restrictedNodegroups
            });

            viewModel.branchListView = new BranchListView({
                el: $('#branch-library'),
                branches: data.branches,
                graphModel: viewModel.graphModel,
                loading: viewModel.loading,
                disableAppendButton: ko.computed(function() {
                    // self.node() && self.node().dirty();
                })
            });

            viewModel.permissionsDesigner = new PermissionDesigner({
                cardTree: viewModel.permissionTree
            });

            viewModel.graphSettingsViewModel = new GraphSettingsViewModel({
                designerViewModel: viewModel,
                graph: viewModel.graph,
                graphModel: viewModel.graphModel,
                ontologyClasses: viewModel.ontologyClasses,
                ontologies: viewModel.ontologies,
                ontologyClass: ko.observable(''),
                iconFilter: ko.observable(''),
                node: viewModel.selectedNode,
                rootNodeColor: ko.observable(''),
                "ontology_namespaces": data.ontology_namespaces,
                onReset: function() {
                    var graph = ko.mapping.toJS(viewModel.graphSettingsViewModel.graph);
                    viewModel.report.configJSON(graph.config);
                    viewModel.report.get('template_id')(graph["template_id"]);
                }
            });

            viewModel.report = new ReportModel(_.extend(data, {
                graphModel: viewModel.graphModel,
                cards: viewModel.cardTree.topCards,
                preview: true
            }));

            viewModel.report.configJSON.subscribe(function(config) {
                var graph = ko.mapping.toJS(viewModel.graphSettingsViewModel.graph);
                graph.config = config;
                ko.mapping.fromJS(graph, viewModel.graphSettingsViewModel.graph);
            });

            viewModel.report.get('template_id').subscribe(function(val) {
                viewModel.graphSettingsViewModel.graph["template_id"](val);
            });

            viewModel.reportLookup = reportLookup;
            viewModel.reportTemplates = _.map(reportLookup, function(report, id) {
                report.id = id;
                return report;
            });

            viewModel.graphTree = new GraphTree({
                graphModel: viewModel.graphModel,
                graphSettings: viewModel.graphSettingsViewModel,
                cardTree: viewModel.cardTree,
                permissionTree: viewModel.permissionTree,
                restrictedNodegroups: data.restrictedNodegroups
            });

            viewModel.graphTree.branchListVisible.subscribe(function(visible) {
                if (visible) {
                    viewModel.branchListView.loadDomainConnections();
                }
            }, this);

            viewModel.loadGraphSettings = function() {
                var self = this;
                viewModel.loading(true);
                $.ajax({
                    type: 'GET',
                    url: arches.urls.graph_settings(data.graphid),
                    data: {'search': true, 'csrfmiddlewaretoken': '{{ csrf_token }}'}})
                    .done(function(data) {
                        self.graphSettingsViewModel.resource_data(data.resources);
                        self.graphSettingsViewModel.icon_data(data.icons);
                        self.graphSettingsViewModel.jsonCache(self.graphSettingsViewModel.jsonData());
                        self.graphSettingsViewModel.contentLoading = viewModel.loading;
                        self.graphSettingsVisible(true);
                        viewModel.loading(false);
                    })
                    .fail(function() {
                        throw 'error loading graph settings';
                    });
            };

            var correspondingCard = function(item, cardTree){
                var cardList = cardTree.cachedFlatTree;
                if (cardList === undefined) {
                    var cardList = cardTree.flattenTree(cardTree.topCards(), []);
                    cardTree.cachedFlatTree = cardList;
                }
                var res;
                var matchingWidget;
                if (item && typeof item !== 'string') {
                    if (item.nodeGroupId) { //if the item is a node in graph tree
                        var matchingCards = _.filter(cardList, function(card){
                            return card.nodegroupid === item.nodeGroupId();
                        });
                        _.each(matchingCards, function(card){
                            var match;
                            match = _.find(card.widgets(), function(widget){
                                return widget.node_id() === item.nodeid;
                            });
                            if (match) {
                                matchingWidget = match;
                            }
                        });
                        if (matchingWidget) {
                            res = matchingWidget;
                        } else {
                            res = matchingCards[0];
                        }
                    } else { //if the item is a card or widget in the card tree
                        res = _.find(cardList, function(card){
                            if (item.nodegroupid) {
                                return card.nodegroupid === item.nodegroupid;
                            } else {
                                return card.nodegroupid === item.node.nodeGroupId();
                            }
                        });
                    }
                }
                return res;

            };

            var correspondingNode = function(card, graphTree){
                var nodeMatch = _.find(graphTree.items(), function(node){
                    if (card.node) {
                        return node.nodeid === card.node_id();
                    } else {
                        return node.nodeGroupId() === card.nodegroupid && node.nodeid === node.nodeGroupId();
                    }
                });
                return nodeMatch;
            };

            var updateGraphSelection = function() {
                if (viewModel.activeTab() === 'card') {
                    viewModel.graphTree.collapseAll();
                    var matchingNode = correspondingNode(viewModel.cardTree.selection(), viewModel.graphTree);
                    if (matchingNode) {
                        viewModel.graphTree.selectItem(matchingNode);
                    }
                }
            };

            var updateCardSelection = function() {
                if (viewModel.activeTab() === 'graph') {
                    var graphTreeSelection = viewModel.graphTree.selectedItems().length > 0 ? viewModel.graphTree.selectedItems()[0] : null;
                    var matchingCard;
                    if (graphTreeSelection) {
                        if (graphTreeSelection.istopnode === true) {
                            viewModel.cardTree.selection(viewModel.cardTree.topCards()[0]);
                        } else {
                            matchingCard = correspondingCard(graphTreeSelection, viewModel.cardTree);
                            if (matchingCard) {
                                viewModel.cardTree.selection(matchingCard);
                                viewModel.cardTree.collapseAll();
                                viewModel.cardTree.expandToRoot(viewModel.cardTree.selection());
                            }
                        }
                    }
                }
            };

            var updatePermissionCardSelection = function() {
                var matchingCard = correspondingCard(viewModel.cardTree.selection(), viewModel.permissionTree);
                if (matchingCard) {
                    viewModel.permissionTree.collapseAll();
                    viewModel.permissionTree.expandToRoot(matchingCard);
                    viewModel.permissionTree.selection.removeAll();
                    matchingCard.selected(true);
                }
            };

            viewModel.cardTree.selection.subscribe(function(){
                updateGraphSelection();
                updatePermissionCardSelection();
            });

            viewModel.graphTree.selectedItems.subscribe(function(){
                updateCardSelection();
                updatePermissionCardSelection();
            });

            if (viewModel.activeTab() === 'graph') {
                viewModel.loadGraphSettings();
                // here we might load data/views asyncronously
            }

            var loadPermissionData = viewModel.activeTab.subscribe(function(tab) {
                // Loads identities and nodegroup permissions when the permissions tab is opened and then disposes the ko.subscribe.
                if (tab === 'permissions') {
                    viewModel.permissionsDesigner.getPermissionManagerData();
                    loadPermissionData.dispose();
                }
            });

            var helpContentLookup = {
                permissions: 'permissions-manager-help',
                graph: 'graph-designer-help',
                card: 'card-manager-help'
            };

            viewModel.activeTab.subscribe(function(tab) {
                viewModel.helpTemplate(helpContentLookup[tab]);
                viewModel.getHelp();
            });

            viewModel.graphView = new GraphView({
                el: $('#graph'),
                graphModel: viewModel.graphModel,
                nodeSize: 15,
                nodeSizeOver: 20,
                labelOffset: 10,
                loading: this.loading
            });

            viewModel.graphModel.on('select-node', function(node) {
                viewModel.graphView.zoomTo(node);
                viewModel.graphTree.expandParentNode(node);
            });

            viewModel.viewState.subscribe(function(state) {
                if (state === 'preview') {
                    viewModel.graphView.resize();
                }
            });


            /**
            * update the sizing of elements on window resize
            */
            var resize = function() {
                $('.grid').height($(window).height() - 208);
                $('#graph').height($(window).height() - 100);
                if (!!viewModel.graphView) {
                    viewModel.graphView.resize();
                }
            };

            $(window).resize(resize);

            resize();

            BaseManagerView.prototype.initialize.apply(this, arguments);
        }
    });

    return new GraphDesignerView();
});
