import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import arches from 'arches';
import reportLookup from 'report-templates';
import viewData from 'view-data';
import data from 'views/graph-designer-data';
import BaseManagerView from 'views/base-manager';
import AlertViewModel from 'viewmodels/alert';
import JsonErrorAlertViewModel from 'viewmodels/alert-json';
import GraphModel from 'models/graph';
import ReportModel from 'models/report';
import GraphTree from 'views/graph/graph-designer/graph-tree';
import NodeFormView from 'views/graph/graph-designer/node-form';
import BranchListView from 'views/graph/graph-manager/branch-list';
import CardTreeViewModel from 'views/graph/graph-designer/card-tree';
import PermissionDesigner from 'views/graph/permission-designer';
import GraphSettingsViewModel from 'viewmodels/graph-settings';
import CardViewModel from 'viewmodels/card';
import 'bindings/resizable-sidepanel';
import 'views/components/simple-switch';
import 'utils/set-csrf-token';
import 'datatype-config-components';


var GraphDesignerView = BaseManagerView.extend({
    initialize: function(options) {
        var viewModel = options.viewModel;
        viewModel.graphid = ko.observable(data.graphid);
        viewModel.activeTab = ko.observable('graph');
        viewModel.viewState = ko.observable('design');
        viewModel.helpTemplate(viewData.help);
        viewModel.graphSettingsVisible = ko.observable(false);
        viewModel.graph = koMapping.fromJS(data['graph']);
        viewModel.sourceGraph = koMapping.fromJS(data['source_graph']);
        viewModel.sourceGraphPublicationDate = new Date(data['source_graph_publication']['published_time']).toLocaleString();
        viewModel.sourceGraphPublicationMostRecentEditDate = data['source_graph_publication_most_recent_edit'] ? new Date(data['source_graph_publication_most_recent_edit']['edit_time']).toLocaleString() : null;
        viewModel.ontologies = ko.observable(data['ontologies']);
        viewModel.ontologyClasses = ko.pureComputed(function(){
            return data['ontologyClasses'].filter((cls) => cls.ontology_id === viewModel.graph.ontology_id());
        });
        viewModel.cardComponents = data.cardComponents;
        viewModel.appliedFunctions = ko.observable(data['appliedFunctions']);
        viewModel.activeLanguageDir = ko.observable(arches.activeLanguageDir);
        viewModel.graphPublicationNotes = ko.observable();
        viewModel.shouldShowUpdatePublishedGraphsButton = ko.observable();
        viewModel.primaryDescriptorFunction = ko.observable(data['primaryDescriptorFunction']);
        viewModel.graphHasUnpublishedChanges = ko.observable(data['graph']['has_unpublished_changes']);
        viewModel.publicationResourceInstanceCount = ko.observable(data['publication_resource_instance_count']);
        viewModel.isGraphActive = ko.observable();

        const url = new URL(window.location);
        if (url.searchParams.has('has_been_redirected_from_draft_graph')) {
            viewModel.alert(new AlertViewModel(
                    'ep-alert-blue', 
                    arches.translations.graphDesignerRedirectFromDraftGraph.title,
                    arches.translations.graphDesignerRedirectFromDraftGraph.text,
                    null,
                    function(){
                        // removes query args without reloading page
                        url.search = '';
                        window.history.replaceState({}, document.title, url.toString());
                    },
                )
            );
        }

        fetch(arches.urls.graph_is_active_api(data.graphid)).then(response => {
            if (response.ok) {
                return response.json();
            }
            else {
                viewModel.alert(new AlertViewModel(
                    'ep-alert-red', 
                    _("Could not obtain the Resource Model active status"),
                    _('Please contact your System Administrator'),
                    null,
                    function(){},
                ));
            }
        }).then(responseJSON => {
            viewModel.isGraphActive(responseJSON);
        });

        viewModel.isGraphActive.subscribe(isGraphActive => {
            $.ajax({
                type: 'POST',
                url: arches.urls.graph_is_active_api(data.graphid),
                data: {'is_active': isGraphActive},
                error: function() {
                    const alert = new AlertViewModel(
                        'ep-alert-red', 
                        arches.translations.resourceGraphChangeActiveStatusError.title,
                        arches.translations.resourceGraphChangeActiveStatusError.text,
                        null,
                        function(){},
                    );

                    viewModel.alert(alert);

                    alert.active.subscribe(function() {
                        window.location.reload();
                    });
                }
            });
        });

        viewModel.hasDirtyWidget = ko.observable();

        viewModel.isDirty = ko.pureComputed(() => {
            let isDirty = false;

            if (viewModel.dirty()) {
                isDirty = true;
            }
            if (viewModel.hasDirtyWidget()) {
                isDirty = true;
            }
            if (viewModel.graphSettingsViewModel && viewModel.graphSettingsViewModel.dirty()) {
                isDirty = true;
            }
            if (viewModel.selectedNode() && viewModel.selectedNode().dirty() && viewModel.selectedNode().istopnode == false) {
                isDirty = true;
            }
            if (ko.unwrap(viewModel.cardTree.selection)) {
                const selection = ko.unwrap(viewModel.cardTree.selection);

                if (selection.model && selection.model.dirty()) {
                    isDirty = true;
                }
                if (selection.card && selection.card.dirty()) {
                    isDirty = true;
                }
            }

            return isDirty;
        });
        
        viewModel.shouldShowGraphPublishButtons = ko.pureComputed(function() {
            return Boolean(!viewModel.isDirty() && viewModel.graphHasUnpublishedChanges());
        });

        viewModel.isNodeDirty = ko.pureComputed(function() {
            return viewModel.selectedNode() && viewModel.selectedNode().dirty() && viewModel.selectedNode().istopnode == false;
        });

        var resources = ko.utils.arrayFilter(viewData.graphs, function(graph) {
            return graph.isresource && !graph.source_identifier_id;
        });
        var graphs = ko.utils.arrayFilter(viewData.graphs, function(graph) {
            return !graph.isresource && !graph.source_identifier_id;
        });

        var newGraph = function(url, data) {
            data = data || {};
            viewModel.loading(true);
            $.ajax({
                type: "POST",
                url: url,
                data: JSON.stringify(data),
                success: function(response) {
                    window.open(arches.urls.graph_designer(response.graphid), '_blank');
                    viewModel.loading(false);
                },
                error: function() {
                    viewModel.loading(false);
                }
            });
        };
        viewModel.newResource = function() {
            newGraph('/graph/new', {isresource: true});
        };
        viewModel.newBranch = function() {
            newGraph('/graph/new', {isresource: false});
        };

        viewModel.exportMappingFile = function() {
            window.open(arches.urls.export_mapping_file(viewModel.graph.graphid()), '_blank');
        };

        viewModel.shouldShowPublishModal = ko.observable(false);

        viewModel.toggleLockedState = function() {
            let url = new URL(window.location.href);

            if (url.searchParams.has('should_show_source_graph')) {
                url.searchParams.delete('should_show_source_graph');
            }
            else {
                url.searchParams.append('should_show_source_graph', true);
            }

            window.location.href = url;
        };

        viewModel.publishGraph = function() {
            viewModel.loading(true);

            $.ajax({
                type: "POST",
                data: JSON.stringify({'notes': viewModel.graphPublicationNotes()}),
                url: arches.urls.publish_graph(viewModel.graph.graphid()),
                complete: function(response, status) {
                    let alert;

                    if (status === 'success') {
                        alert = new AlertViewModel(
                            'ep-alert-blue', 
                            response.responseJSON.title, 
                            response.responseJSON.message,
                            null,
                            function(){},
                        );
                    }
                    else {
                        alert = new JsonErrorAlertViewModel(
                            'ep-alert-red', 
                            response.responseJSON,
                            null,
                            function(){},
                        );
                    }

                    // must reload window since this draft_graph has been deleted
                    alert.active.subscribe(function() {
                        window.location.reload();
                    });
                    viewModel.alert(alert);

                    // set max z-index on card alert panel so user can acknowledge that graph has been updated && trigger page reload
                    const cardAlertPanel = document.querySelector('#card-alert-panel');
                    cardAlertPanel.style.zIndex = 2147483647;
                    
                    viewModel.graphPublicationNotes(null);
                    viewModel.shouldShowPublishModal(false);
                }
            });
        };

        viewModel.showRevertGraphAlert = function() {
            viewModel.alert(new AlertViewModel(
                'ep-alert-red', 
                arches.translations.confirmGraphRevert.title, 
                arches.translations.confirmGraphRevert.text,
                function() {}, 
                viewModel.revertGraph,
            ));
        };

        viewModel.revertGraph = function() {
            viewModel.loading(true);

            $.ajax({
                type: "POST",
                url: arches.urls.revert_graph(viewModel.graph.graphid()),
                complete: function(response, status) {
                    if (status === 'success') { window.location.reload(); }
                    else {
                        viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                    }
                }
            });
        };

        viewModel.showRestoreStateFromSerializedGraphAlert = function() {
            viewModel.alert(new AlertViewModel(
                'ep-alert-red', 
                arches.translations.confirmGraphRevert.title, 
                arches.translations.confirmGraphRevert.text,
                function() {}, 
                viewModel.restoreStateFromSerializedGraph,
            ));
        };

        viewModel.restoreStateFromSerializedGraph = function() {
            viewModel.loading(true);

            $.ajax({
                type: "POST",
                url: arches.urls.restore_state_from_serialized_graph(viewModel.graph.graphid()),
                complete: function(response, status) {
                    if (status === 'success') { window.location.reload(); }
                    else {
                        viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                    }
                }
            });
        };

        viewModel.showUpdatePublishedGraphsModal = function() {
            viewModel.shouldShowUpdatePublishedGraphsButton(true);
            viewModel.shouldShowPublishModal(true);
        };

        viewModel.updatePublishedGraphs = function() {
            viewModel.loading(true);

            $.ajax({
                type: "POST",
                data: JSON.stringify({'notes': viewModel.graphPublicationNotes()}),
                url: arches.urls.update_published_graphs(viewModel.graph.graphid()),
                complete: function(response, status) {
                    let alert;

                    if (status === 'success') {
                        alert = new AlertViewModel(
                            'ep-alert-blue', 
                            response.responseJSON.title, 
                            response.responseJSON.message,
                            null,
                            function(){},
                        );
                    }
                    else {
                        alert = new JsonErrorAlertViewModel(
                            'ep-alert-red', 
                            response.responseJSON,
                            null,
                            function(){},
                        );
                    }

                    // must reload window since this draft_graph has been deleted
                    alert.active.subscribe(function() {
                        window.location.reload();
                    });
                    viewModel.alert(alert);

                    // set max z-index on card alert panel so user can acknowledge that graph has been updated && trigger page reload
                    const cardAlertPanel = document.querySelector('#card-alert-panel');
                    cardAlertPanel.style.zIndex = 2147483647;
                    
                    viewModel.shouldShowUpdatePublishedGraphsButton(false);
                    viewModel.graphPublicationNotes(null);
                    viewModel.shouldShowPublishModal(false);
                }
            });
        };

        viewModel.deleteGraph = function() {
            viewModel.alert(new AlertViewModel(
                'ep-alert-red', 
                arches.translations.confirmGraphDelete.title, 
                arches.translations.confirmGraphDelete.text,
                function() {
                    return;
                }, function(){
                    viewModel.loading(true);
                    $.ajax({
                        type: "DELETE",
                        url: arches.urls.delete_graph(viewModel.graph.source_identifier_id() || viewModel.graph.graphid()),
                        complete: function(response, status) {
                            viewModel.loading(false);
                            if (status === 'success') {
                                window.location = arches.urls.graph;
                            } else {
                                viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                            }
                        }
                    });
                }
            ));
        };
        viewModel.cloneGraph = function() {
            newGraph(arches.urls.clone_graph(viewModel.graph.source_identifier_id() || viewModel.graph.graphid()));
        };
        viewModel.exportGraph = function() {
            window.open(arches.urls.export_graph(viewModel.graph.source_identifier_id() || viewModel.graph.graphid()), '_blank');
        };
        viewModel.importGraph = function(data, e) {
            var formData = new FormData();
            formData.append("importedGraph", e.target.files[0]);

            $.ajax({
                type: "POST",
                url: '/graph/import/',
                processData: false,
                data: formData,
                cache: false,
                contentType: false,
                success: function(response) {
                    if (response[0].length != 0) {
                        // eslint-disable-next-line no-constant-condition
                        if (typeof(response[0])) {
                            response = response[0].join('<br />');
                        }
                        viewModel.alert(new AlertViewModel('ep-alert-red', arches.translations.graphImportFailed.title, response));
                    } else {
                        viewModel.loading(false);
                        window.open(arches.urls.graph_designer(response[1].graph_id), '_blank');
                    }
                },
                error: function(response) {
                    viewModel.alert(
                        new AlertViewModel('ep-alert-red', arches.translations.graphImportFailed.title, arches.translations.pleaseContactSystemAdministrator)
                    );
                    viewModel.loading(false);
                },
            });
        };
        viewModel.importButtonClick = function() {
            $("#fileupload").trigger('click');
        };
        viewModel.deleteInstances = function() {
            viewModel.alert(new AlertViewModel(
                'ep-alert-red', 
                arches.translations.confirmAllResourceDelete.title, 
                arches.translations.confirmAllResourceDelete.text, 
                function() {
                    return;
                }, function(){
                    viewModel.loading(true);
                    $.ajax({
                        type: "DELETE",
                        url: arches.urls.delete_instances(viewModel.graph.source_identifier_id() || viewModel.graph.graphid()),
                        complete: function(response, status) {
                            viewModel.loading(false);
                            if (status === 'success') {
                                viewModel.alert(new AlertViewModel('ep-alert-blue', response.responseJSON.title, response.responseJSON.message));
                            } else {
                                viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                            }
                        }
                    });
                }
            ));
        };
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

        viewModel.graphModel.on('error', function(response) {
            viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
        });

        viewModel.selectedNode = viewModel.graphModel.get('selectedNode');
        viewModel.updatedCardinalityData = ko.observable();

        // ctrl+S to save any edited/dirty nodes 
        var keyListener = function(e) {
            if (e.ctrlKey && e.key === "s") {
                e.preventDefault();
                if (viewModel.isNodeDirty() || viewModel.graphSettingsViewModel.dirty()) {
                    viewModel.saveSelectedNode();
                }
            }
        };
        document.addEventListener("keydown", keyListener)
        // dispose of eventlistener
        this.dispose = function(){
            document.removeEventListener("keydown", keyListener);
        };

        viewModel.saveNode = function(node) {
            if (node) {
                viewModel.loading(true);
                node.save(function(data) {
                    if (data.responseJSON.success === false || data.status === 500) {
                        viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', data.responseJSON));
                    }
                    else {
                        viewModel.cardTree.updateCards(viewModel.selectedNode().nodeGroupId(), data.responseJSON);
                        viewModel.permissionTree.updateCards(viewModel.selectedNode().nodeGroupId(), data.responseJSON);
                        viewModel.updatedCardinalityData([data.responseJSON, viewModel.graphSettingsViewModel]);
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

        viewModel.saveCardEdits = function(card) {
            card.save();
        };

        viewModel.cardTree = new CardTreeViewModel({
            graph: viewModel.graph,
            appliedFunctions: viewModel.appliedFunctions,
            primaryDescriptorFunction: viewModel.primaryDescriptorFunction,
            graphModel: viewModel.graphModel
        });

        viewModel.permissionTree = new CardTreeViewModel({
            graph: koMapping.fromJS(data.source_graph),
            graphModel: viewModel.graphModel,
            isPermissionTree: true,
            appliedFunctions: viewModel.appliedFunctions,
            primaryDescriptorFunction: viewModel.primaryDescriptorFunction,
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
            appliedFunctions: viewModel.appliedFunctions,
            primaryDescriptorFunction: viewModel.primaryDescriptorFunction,
            updatedCardinalityData: viewModel.updatedCardinalityData,
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
            rootNodeColor: ko.observable(''),
            "ontology_namespaces": data.ontology_namespaces,
            onReset: function() {
                var graph = koMapping.toJS(viewModel.graphSettingsViewModel.graph);
                viewModel.report.resetConfigs(graph.config);

                // only reset the template if it's been changed
                if (viewModel.report.get('template_id')() !== graph["template_id"]) {
                    viewModel.report.get('template_id')(graph["template_id"]);
                }
            },
            onSave: function() {
                // adds event to trigger dirty state in graph-designer
                document.dispatchEvent(
                    new Event('graphSettingsSave')
                );
            }
        });

        viewModel.report = new ReportModel(_.extend(data, {
            graphModel: viewModel.graphModel,
            cards: viewModel.cardTree.topCards,
            preview: true
        }));

        viewModel.report.configJSON.subscribe(function(config) {
            var graph = koMapping.toJS(viewModel.graphSettingsViewModel.graph);
            graph.config = koMapping.toJS(config);
            koMapping.fromJS(graph, viewModel.graphSettingsViewModel.graph);
        });

        viewModel.report.configJSON.extend({deferred: true});

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
            appliedFunctions: viewModel.appliedFunctions,
            primaryDescriptorFunction: viewModel.primaryDescriptorFunction,
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
                cardList = cardTree.flattenTree(cardTree.topCards(), []);
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
            var nodeMatch;
            nodeMatch = _.find(graphTree.items(), function(node){
                if (card) {
                    if (card.node) {
                        return node.nodeid === card.node_id();
                    } else {
                        return node.nodeGroupId() === card.nodegroupid && node.nodeid === node.nodeGroupId();
                    }
                }
            });
            return nodeMatch;
        };

        var updateGraphSelection = function() {
            var matchingNode = correspondingNode(viewModel.cardTree.selection(), viewModel.graphTree);
            if (matchingNode) {
                viewModel.graphTree.selectItem(matchingNode);
            }
        };

        var updateCardSelection = function() {
            var graphTreeSelection = viewModel.graphTree.selectedItems().length > 0 ? viewModel.graphTree.selectedItems()[0] : null;
            var matchingCard;
            if (graphTreeSelection) {
                if (graphTreeSelection.istopnode === true) {
                    viewModel.cardTree.selection(viewModel.cardTree.topCards()[0]);
                } else {
                    matchingCard = correspondingCard(graphTreeSelection, viewModel.cardTree);
                    if (matchingCard) {
                        viewModel.cardTree.selection(matchingCard);
                        viewModel.cardTree.expandToRoot(viewModel.cardTree.selection());
                    }
                }
            }
        };

        var updatePermissionCardSelection = function() {
            var matchingCard = correspondingCard(viewModel.cardTree.selection(), viewModel.permissionTree);
            if (matchingCard) {
                viewModel.permissionTree.expandToRoot(matchingCard);
                viewModel.permissionTree.selection.removeAll();
                matchingCard.selectChildCards();
            }
        };

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
            permissions: {
                'title': 'xxxx', // dynamic title loading not implemented
                'template': 'permissions-tab-help',
            },
            graph: {
                'title': 'xxxx', // dynamic title loading not implemented
                'template': 'graph-tab-help',
            },
            card: {
                'title': 'xxxx', // dynamic title loading not implemented
                'template': 'cards-tab-help',
            }
        };

        viewModel.activeTab.subscribe(function(tab) {
            viewModel.helpTemplate(helpContentLookup[tab]['template']);
            viewModel.getHelp(viewModel.helpTemplate());
            switch (tab) {
            case 'card':
                updateCardSelection();
                break;
            case 'graph':
                updateGraphSelection();
                break;
            case 'permissions':
                updatePermissionCardSelection();
                break;
            default:
                return;
            }
        });

        viewModel.graphModel.on('select-node', function(node) {
            viewModel.graphTree.expandParentNode(node);
        });

        document.addEventListener('appendBranch', () => viewModel.graphHasUnpublishedChanges(true));
        document.addEventListener('addChildNode', () => viewModel.graphHasUnpublishedChanges(true));
        document.addEventListener('deleteNode', () => viewModel.graphHasUnpublishedChanges(true));
        document.addEventListener('reorderNodes', () => viewModel.graphHasUnpublishedChanges(true));
        document.addEventListener('reorderCards', () => viewModel.graphHasUnpublishedChanges(true));
        document.addEventListener('cardSave', () => viewModel.graphHasUnpublishedChanges(true));
        document.addEventListener('nodeSave', () => viewModel.graphHasUnpublishedChanges(true));
        document.addEventListener('permissionsSave', () => viewModel.graphHasUnpublishedChanges(true));
        document.addEventListener('graphSettingsSave', () => viewModel.graphHasUnpublishedChanges(true));
        
        BaseManagerView.prototype.initialize.apply(this, arguments);
    }
});

export default new GraphDesignerView();
