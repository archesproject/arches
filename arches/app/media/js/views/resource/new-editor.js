define([
    'jquery',
    'underscore',
    'knockout',
    'moment',
    'views/base-manager',
    'viewmodels/alert',
    'models/graph',
    'models/report',
    'viewmodels/card',
    'viewmodels/provisional-tile',
    'arches',
    'resource-editor-data',
    'views/search/search-results',
    'views/resource/related-resources-manager',
    'report-templates',
    'bindings/resizable-sidepanel',
    'bindings/sortable',
    'widgets',
    'card-components'
], function($, _, ko, moment, BaseManagerView, AlertViewModel, GraphModel, ReportModel, CardViewModel, ProvisionalTileViewModel, arches, data, searchResults, RelatedResourcesManager, reportLookup) {
    var handlers = {
        'after-update': [],
        'tile-reset': []
    };
    var tiles = data.tiles;
    var filter = ko.observable('');
    var loading = ko.observable(false);
    var selection = ko.observable('root');
    var scrollTo = ko.observable();
    var displayname = ko.observable(data.displayname);
    var resourceId = ko.observable(data.resourceid);
    var selectedTile = ko.computed(function() {
        var item = selection();
        if (item && typeof item !== 'string') {
            if (item.tileid) {
                return item;
            }
            return item.getNewTile();
        }
    });
    var addableCards = ko.computed(function() {
        var items = [];
        if (selectedTile()) {
            _.each(selectedTile().cards, function(card) {
                if (card && card.canAdd()) {
                    items.push(card);
                }
            });
            return items;
        }
    });
    var provisionalTileViewModel = new ProvisionalTileViewModel({tile: selectedTile, reviewer: data.user_is_reviewer});

    var flattenTree = function(parents, flatList) {
        _.each(ko.unwrap(parents), function(parent) {
            flatList.push(parent);
            var childrenKey = parent.tiles ? 'tiles' : 'cards';
            flattenTree(
                ko.unwrap(parent[childrenKey]),
                flatList
            );
        });
        return flatList;
    };

    var toggleAll = function(state) {
        var nodes = flattenTree(vm.topCards, []);
        _.each(nodes, function(node) {
            node.expanded(state);
        });
        if (state) {
            vm.rootExpanded(true);
        }
    };
    var createLookup = function(list, idKey) {
        return _.reduce(list, function(lookup, item) {
            lookup[item[idKey]] = item;
            return lookup;
        }, {});
    };

    var graphModel = new GraphModel({
        data: {nodes: data.nodes, nodegroups: data.nodegroups, edges: []},
        datatypes: data.datatypes
    });

    var vm = {
        loading: loading,
        scrollTo: scrollTo,
        filterEnterKeyHandler: function(context, e) {
            if (e.keyCode === 13) {
                var highlightedItems = _.filter(flattenTree(vm.topCards, []), function(item) {
                    return item.highlight && item.highlight();
                });
                var previousItem = scrollTo();
                scrollTo(null);
                if (highlightedItems.length > 0) {
                    var scrollIndex = 0;
                    var previousIndex = highlightedItems.indexOf(previousItem);
                    if (previousItem && highlightedItems[previousIndex+1]) {
                        scrollIndex = previousIndex + 1;
                    }
                    scrollTo(highlightedItems[scrollIndex]);
                }
                return false;
            }
            return true;
        },
        widgetLookup: createLookup(data.widgets, 'widgetid'),
        cardComponentLookup: createLookup(data.cardComponents, 'componentid'),
        nodeLookup: createLookup(graphModel.get('nodes')(), 'nodeid'),
        graphid: data.graphid,
        graphname: data.graphname,
        issystemsettings: data.issystemsettings,
        reviewer: data.userisreviewer,
        graphiconclass: data.graphiconclass,
        relationship_types: data.relationship_types,
        graph: {
            graphid: data.graphid,
            name: data.graphname,
            iconclass: data.graphiconclass,
            ontologyclass: data.ontologyclass
        },
        displayname: displayname,
        expandAll: function() {
            toggleAll(true);
        },
        collapseAll: function() {
            toggleAll(false);
        },
        rootExpanded: ko.observable(true),
        topCards: _.filter(data.cards, function(card) {
            var nodegroup = _.find(data.nodegroups, function(group) {
                return group.nodegroupid === card.nodegroup_id;
            });
            return !nodegroup || !nodegroup.parentnodegroup_id;
        }).map(function(card) {
            return new CardViewModel({
                card: card,
                graphModel: graphModel,
                tile: null,
                resourceId: resourceId,
                displayname: displayname,
                handlers: handlers,
                cards: data.cards,
                tiles: tiles,
                selection: selection,
                scrollTo: scrollTo,
                loading: loading,
                filter: filter,
                provisionalTileViewModel: provisionalTileViewModel,
                cardwidgets: data.cardwidgets,
                userisreviewer: data.userisreviewer
            });
        }),
        selection: selection,
        selectedTile: selectedTile,
        selectedCard: ko.computed(function() {
            var item = selection();
            if (item && typeof item !== 'string') {
                if (item.tileid) {
                    return item.parent;
                }
                return item;
            }
        }),
        addableCards: ko.computed(function() {
            var tile = selectedTile();
            return _.filter(tile ? tile.cards : [], function(card) {
                return card.canAdd();
            });
        }),
        provisionalTileViewModel: provisionalTileViewModel,
        filter: filter,
        on: function(eventName, handler) {
            if (handlers[eventName]) {
                handlers[eventName].push(handler);
            }
        },
        resourceId: resourceId,
        reportLookup: reportLookup,
        copyResource: function() {
            if (resourceId()) {
                vm.menuActive(false);
                loading(true);
                $.ajax({
                    type: "GET",
                    url: arches.urls.resource_copy.replace('//', '/' + resourceId() + '/'),
                    success: function() {
                        vm.alert(new AlertViewModel('ep-alert-blue', arches.resourceCopySuccess.title, '', null, function(){}));
                    },
                    error: function() {
                        vm.alert(new AlertViewModel('ep-alert-red', arches.resourceCopyFailed.title, arches.resourceCopyFailed.text, null, function(){}));
                    },
                    complete: function() {
                        loading(false);
                    },
                });
            }
        },
        deleteResource: function() {
            if (resourceId()) {
                vm.menuActive(false);
                vm.alert(new AlertViewModel('ep-alert-red', arches.confirmResourceDelete.title, arches.confirmResourceDelete.text, function() {
                    return;
                }, function(){
                    loading(true);
                    $.ajax({
                        type: "DELETE",
                        url: arches.urls.resource_editor + resourceId(),
                        complete: function(request, status) {
                            loading(false);
                            if (status === 'success') {
                                vm.navigate(arches.urls.resource);
                            }
                        },
                    });
                }));
            }
        },
        deleteTile: function(tile) {
            tile.deleteTile(function(response) {
                vm.alert(new AlertViewModel('ep-alert-red', response.responseJSON.message[0], response.responseJSON.message[1], null, function(){}));
            });
        },
        saveTile: function(tile) {
            tile.save(function(response) {
                vm.alert(new AlertViewModel('ep-alert-red', response.responseJSON.message[0], response.responseJSON.message[1], null, function(){}));
            });
        },
        viewEditHistory: function() {
            if (resourceId()) {
                vm.menuActive(false);
                vm.navigate(arches.urls.get_resource_edit_log(resourceId()));
            }
        },
        viewReport: function(print) {
            if (resourceId()) {
                var url = arches.urls.resource_report + resourceId();
                if (print) {
                    url = url + '?print';
                }
                vm.menuActive(false);
                window.open(url, "_blank");
            }
        }
    };

    vm.report = null;
    vm.report = new ReportModel(_.extend(data, {graphModel: graphModel, cards: vm.topCards}));

    vm.resourceId.subscribe(function(){
        //switches the url from 'create-resource' once the resource id is available
        history.pushState({}, '', arches.urls.resource_editor + resourceId());
    });

    vm.showRelatedResourcesManager = function(){
        if (vm.graph.domain_connections == undefined) {
            $.ajax({
                url: arches.urls.relatable_resources,
                data: {graphid: vm.graphid}
            }).done(function(relatable){
                vm.graph.relatable_resources = relatable;
                $.ajax({
                    url: arches.urls.get_domain_connections(vm.graphid),
                    data: {"ontology_class": vm.graph.ontologyclass}
                }).done(function(data){
                    vm.graph.domain_connections = data;
                    vm.relatedResourcesManager = new RelatedResourcesManager({
                        searchResults: new searchResults(),
                        resourceEditorContext: true,
                        editing_instance_id: vm.resourceId(),
                        relationship_types: vm.relationship_types,
                        graph: vm.graph
                    });
                    vm.selection('related-resources');
                });
            });

        } else {
            vm.selection('related-resources');
        }
    };


    vm.selectionBreadcrumbs = ko.computed(function() {
        var item = vm.selectedTile();
        var crumbs = [];
        if (item) {
            while (item.parent) {
                item = item.parent;
                crumbs.unshift(item);
            }
        }
        return crumbs;
    });

    return new BaseManagerView({
        viewModel: vm
    });
});
