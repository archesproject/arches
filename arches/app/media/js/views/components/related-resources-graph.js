define([
    'arches',
    'knockout',
    'views/components/workbench',
    'bindings/cytoscape'
], function(arches, ko, WorkbenchViewmodel) {
    return ko.components.register('related-resources-graph', {
        viewModel: function(params) {
            var self = this;
            var layout = {
                name: "cose",
                animate: true,
                animationThreshold: 10
            };
            var fitPadding = 100;

            this.viz = ko.observable();
            this.cytoscapeConfig = ko.observable();
            this.focusResourceId = ko.isObservable(params.resourceId) ? params.resourceId : ko.observable(params.resourceId);
            this.selection = ko.observable();
            this.selectionMode = ko.observable('information');
            this.elements = ko.observableArray();
            this.informationElement = ko.observable();
            this.legendEntries = ko.observableArray();
            this.nodeSearchFilter = ko.observable('');
            this.expandedSearchId = ko.observable();
            this.searchNodes = ko.computed(function() {
                var filter = self.nodeSearchFilter();
                var elements = self.elements();
                var viz = self.viz();
                var filteredNodes = [];
                elements.forEach(function(element) {
                    if (element.isNode()) {
                        var data = element.data();
                        if (!data.shownRelationsCount) data.shownRelationsCount = ko.observable();
                        if (data.displayname.toLowerCase().indexOf(filter) !== -1) {
                            data.graph = resourceTypeLookup[data.graph_id];
                            data.shownRelationsCount(viz.edges('[source = "' + data.id + '"]').length +
                                viz.edges('[target = "' + data.id + '"]'). length);
                            filteredNodes.push(data);
                        }
                    }
                });
                return filteredNodes;
            });
            // strips URL from relationship labels, if present, for presentation
            var getRelationshipLabel = function(edgeData) {
                var label;
                try {
                    var url = new window.URL(edgeData.relationshiptype_label);
                    label = url.pathname.split('/')[url.pathname.split('/').length - 1];
                } catch (e) {
                    label = edgeData.relationshiptype_label;
                }
                return label;
            };
            this.informationElementRelationships = ko.computed(function() {
                var relationships = [];
                var informationElement = self.informationElement();
                var viz = self.viz();
                self.elements();
                if (informationElement && viz && !informationElement.source) {
                    var sourceEdges = viz.edges('[source = "' + informationElement.id + '"]');
                    var targetEdges = viz.edges('[target = "' + informationElement.id + '"]');
                    var addRelationship = function(edge, nodeType) {
                        var edgeData = edge.data();
                        var nodeData = edge[nodeType]().data();
                        var label = getRelationshipLabel(edgeData);

                        relationships.push({
                            label: label,
                            node: nodeData,
                            edge: edgeData,
                            informationElement: self.informationElement
                        });
                    };
                    sourceEdges.forEach(function(edge) {
                        addRelationship(edge, 'target');
                    });
                    targetEdges.forEach(function(edge) {
                        addRelationship(edge, 'source');
                    });
                }
                return relationships;
            });
            this.edgeInformation = ko.computed(function() {
                var informationElement = self.informationElement();
                var viz = self.viz();
                if (informationElement && viz && informationElement.source) {
                    var sourceData = viz.getElementById(informationElement.source).data();
                    var targetData = viz.getElementById(informationElement.target).data();
                    return {
                        label: getRelationshipLabel(informationElement),
                        source: sourceData,
                        sourceGraph: resourceTypeLookup[sourceData['graph_id']],
                        target: targetData,
                        targetGraph: resourceTypeLookup[targetData['graph_id']]
                    };
                }
            });

            WorkbenchViewmodel.apply(this, [params]);

            var getResourceRelations = function(resourceId) {
                var url = arches.urls.related_resources + resourceId + '?paginate=false';
                return window.fetch(url);
            };
            var resourceTypeLookup = {};
            var dataToElement = function(data) {
                data.source = data.resourceinstanceidfrom;
                data.target = data.resourceinstanceidto;
                if (data.source) {
                    data.id = data.source + data.target;
                } else {
                    data.id = data.resourceinstanceid;
                    data.totalRelations = data.total_relations.value;
                }
                var classes = [];
                if (data.graph_id) classes.push(resourceTypeLookup[data.graph_id].className);
                if (data.focus) classes.push('focus');
                return {
                    data: data,
                    classes: classes,
                    selected: data.focus
                };
            };
            this.expandNode = function(node) {
                if (node.id) getResourceRelations(node.id)
                    .then(function(response) {
                        return response.json();
                    })
                    .then(function(result) {
                        var viz = self.viz();
                        var elements = result.related_resources.concat(result.resource_relationships)
                            .map(dataToElement)
                            .filter(function(element) {
                                var elements = viz.getElementById(element.data.id);
                                if (element.source) elements = elements.concat(
                                    viz.getElementById(element.source + element.target),
                                    viz.getElementById(element.target + element.source)
                                );
                                return elements.length === 0;
                            });
                        viz.add(elements);
                        self.elements(viz.elements());
                        viz.layout(layout).run();
                        viz.fit(null, fitPadding);
                    });
            };
            var getStyle = function() {
                self.legendEntries([]);
                var nodeSize = 86;
                var lineColor = '#606060';
                var styles = [{
                    "selector": "node",
                    "style": {
                        "content": "data(displayname)",
                        "font-size": "18px",
                        "width": nodeSize,
                        "height": nodeSize,
                        "text-valign": "center",
                        "text-halign": "center",
                        "border-color": lineColor,
                        "border-width": 1
                    }
                }, {
                    "selector": "node.focus",
                    "style": {
                        "font-weight": "bold"
                    }
                }, {
                    "selector": "node:selected",
                    "style": {
                        "border-width": 5
                    }
                }, {
                    "selector": "edge",
                    "style": {
                        "line-color": lineColor
                    }
                }, {
                    "selector": "edge:selected",
                    "style": {
                        "width": 6,
                        "line-color": lineColor
                    }
                }];
                for (var resourceId in resourceTypeLookup) {
                    var color = resourceTypeLookup[resourceId].fillColor || '#CCCCCC';
                    var style = {
                        "selector": "node." + resourceTypeLookup[resourceId].className,
                        "style": {
                            "background-color": color
                        }
                    };
                    styles.push(style);
                    self.legendEntries.push(resourceTypeLookup[resourceId]);
                }
                return styles;
            };
            var updateCytoscapeConfig = function(elements) {
                self.cytoscapeConfig({
                    selectionType: 'single',
                    elements: elements,
                    layout: layout,
                    style: getStyle()
                });
            };
            var updateFocusResource = function() {
                var resourceId = self.focusResourceId();
                if (resourceId) {
                    self.viz(null);
                    getResourceRelations(resourceId)
                        .then(function(response) {
                            return response.json();
                        })
                        .then(function(result) {
                            var i = 0;
                            for (var resourceId in result.node_config_lookup) {
                                result.node_config_lookup[resourceId].className = 'resource-type-' + i;
                                i++;
                            }
                            resourceTypeLookup = result.node_config_lookup;
                            result.resource_instance.focus = true;
                            result.resource_instance['total_relations'] = {
                                value: result.resource_relationships.length
                            };
                            var elements = [dataToElement(result.resource_instance)]
                                .concat(
                                    result.related_resources.concat(result.resource_relationships)
                                        .map(dataToElement)
                                );
                            self.selection(elements[0].data);
                            updateCytoscapeConfig(elements);
                            self.elements(self.viz().elements());
                        });
                }
            };

            this.focusResourceId.subscribe(updateFocusResource);
            this.viz.subscribe(function(viz) {
                if (!viz) {
                    self.cytoscapeConfig(null);
                    self.selection(null);
                }
                else {
                    viz.on('select', 'node, edge', function(e) {
                        // prevents multiple selection
                        viz.elements().not(e.target).unselect();

                        self.selection(e.target.data());
                    });
                    viz.on('unselect', 'node, edge', function() {
                        self.selection(null);
                    });
                }
            });

            this.activeTab.subscribe(function() {
                var viz = self.viz();
                if (viz) viz.resize();
            });

            this.selection.subscribe(function(selection) {
                var mode = self.selectionMode();
                var viz = self.viz();
                if (selection) switch (mode) {
                case 'expand':
                    if (selection.source) viz.elements().unselect();
                    else self.expandNode(selection);
                    break;
                case 'delete':
                    var element = viz.getElementById(selection.id);
                    var informationElement = self.informationElement();
                    var informationElementId = informationElement ? informationElement.id : null;
                    if (!selection.source) viz.edges().forEach(function(edge) {
                        if (edge.source().id() === selection.id ||
                            edge.target().id() === selection.id) {
                            if (edge.id() === informationElementId) self.informationElement(null);
                            viz.remove(edge);
                            self.elements.remove(edge);
                        }
                    });
                    if (selection.id === informationElementId) self.informationElement(null);
                    viz.remove(element);
                    self.elements.remove(element);
                    viz.fit(null, fitPadding);
                    break;
                case 'focus':
                    if (selection.source) viz.elements().unselect();
                    else {
                        self.focusResourceId(selection.id);
                        self.informationElement(selection);
                    }
                    break;
                default:
                    self.informationElement(selection);
                    break;
                }
            });

            self.informationElement.subscribe(function(data) {
                var viz = self.viz();
                if (data) {
                    if (viz) {
                        var element = viz.getElementById(data.id);
                        if (!element.selected()) {
                            self.selectionMode('information');
                            element.select();
                        }
                    }
                    self.activeTab('information');
                }
            });

            this.selectionMode.subscribe(function() {
                var viz = self.viz();
                viz.elements().unselect();
            });

            updateFocusResource();
        },
        template: { require: 'text!templates/views/components/related-resources-graph.htm' }
    });
});
