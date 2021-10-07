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
                name: "cola",
                animate: true,
                directed: true,
                edgeLength: 200
            };

            this.viz = ko.observable();
            this.cytoscapeConfig = ko.observable();
            this.focusResourceId = ko.isObservable(params.resourceId) ?
                params.resourceId :
                ko.observable(params.resourceId);
            this.selection = ko.observable();
            this.selectionMode = ko.observable('information');
            this.elements = ko.observableArray();
            this.informationElement = ko.observable();
            this.informationGraph = ko.computed(function() {
                var informationElement = self.informationElement();
                if (informationElement && informationElement.graph_id)
                    return resourceTypeLookup[informationElement.graph_id];
                return {};
            });
            this.viewInformationNodeReport = function() {
                var informationElement = self.informationElement();
                if (informationElement)
                    window.open(arches.urls.resource_report + informationElement.id);
            };
            this.editInformationNode = function() {
                var informationElement = self.informationElement();
                if (informationElement)
                    window.open(arches.urls.resource_editor + informationElement.id);
            };
            this.hoverElementId = ko.observable();
            this.legendEntries = ko.computed(function() {
                var elements = self.elements();
                var entries = [];
                for (var resourceTypeId in resourceTypeLookup) {
                    if (elements.filter(function(element) {
                        return element.data('graph_id') === resourceTypeId;
                    }).length > 0) entries.push(resourceTypeLookup[resourceTypeId]);
                }
                return entries;
            });
            this.nodeSearchFilter = ko.observable('');
            this.expandedSearchId = ko.observable();
            this.searchNodes = ko.computed(function() {
                var filter = self.nodeSearchFilter();
                var elements = self.elements();
                var viz = self.viz();
                var filteredNodes = [];
                if (viz) elements.forEach(function(element) {
                    if (element.isNode()) {
                        var data = element.data();
                        if (!data.shownRelationsCount) data.shownRelationsCount = ko.observable();
                        if (data.displayname.toLowerCase().indexOf(filter) !== -1) {
                            data.graph = resourceTypeLookup[data.graph_id];
                            // excludes target relationships back to node, to prevent duplicates
                            data.shownRelationsCount(viz.edges('[source = "' + data.id + '"]').length +
                                viz.edges('[target = "' + data.id + '"][source != "' + data.id + '"]'). length);
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
                            informationElement: self.informationElement,
                            hoverElementId: self.hoverElementId
                        });
                    };
                    sourceEdges.forEach(function(edge) {
                        addRelationship(edge, 'target');
                    });
                    targetEdges.forEach(function(edge) {
                        // excludes target relationships back to node, to prevent duplicates
                        if (edge.source().id() !== edge.target().id())
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
                        id: informationElement.id,
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
                    data.id = data.resourcexid;
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
            this.refreshLayout = function() {
                var viz = self.viz();
                if (viz) {
                    viz.elements().makeLayout(layout).run();
                }
            };
            this.addMissingNodes = function(elements){
                var nodesReferencedByEdges = [];
                elements.forEach(function(ele){
                    if(!!ele.data.source){
                        nodesReferencedByEdges.push(ele.data.source);
                    }
                    if(!!ele.data.target){
                        nodesReferencedByEdges.push(ele.data.target);
                    }
                });
                var relatedResourceIds = elements.filter(function(ele){
                    return !!ele.data.resourceinstanceid;
                }).map(function(ele){
                    return ele.data.resourceinstanceid;
                });
                // add reference to missing nodes
                nodesReferencedByEdges.forEach(function(resourceId){
                    if(!relatedResourceIds.includes(resourceId)){
                        elements.push({
                            'classes':[],
                            'data':{
                                'graph_id': 'undefined',
                                'id': resourceId,
                                'target': undefined,
                                'source': undefined,
                                'displayname': '',
                                'totalRelations': 1
                            },
                            'selected': undefined
                        });
                        relatedResourceIds.push(resourceId);
                    }
                });
                return elements;
            };
            this.expandNode = function(node) {
                var viz = self.viz();
                var position;
                if (viz) {
                    position = self.viz().getElementById(node.id).position();
                }
                if (node.id) getResourceRelations(node.id)
                    .then(function(response) {
                        return response.json();
                    })
                    .then(function(result) {
                        var elements = result.related_resources.concat(result.resource_relationships)
                            .map(function(data) {
                                var element = dataToElement(data);
                                if (!data.source && position) {
                                    element.position = {
                                        x: position.x,
                                        y: position.y
                                    };
                                }
                                return element;
                            });    
                        elements = self.addMissingNodes(elements)
                            .filter(function(element) {
                                return viz.getElementById(element.data.id).length === 0;
                            });
                        self.viz().getElementById(node.id).lock();
                        viz.add(elements);
                        self.elements(viz.elements());
                        var vizLayout = viz.elements().makeLayout(layout);
                        vizLayout.on("layoutstop", function() {
                            viz.nodes().unlock();
                        });
                        vizLayout.run();
                    });
            };
            var getStyle = function() {
                var nodeSize = 60;
                var borderColor = '#115170';
                var borderHighlightColor = '#023047';
                var borderSelectedColor = '#000F16';
                var lineColor = '#BFBEBE';
                var selectedLineColor = '#023047';
                var borderWidth = 1;
                var hoverBorderWidth = 4;
                var selectedBorderWidth = 4;
                var styles = [{
                    "selector": "node",
                    "style": {
                        "content": "data(displayname)",
                        "font-size": "18px",
                        "width": nodeSize,
                        "height": nodeSize,
                        "text-valign": "center",
                        "text-halign": "center",
                        "border-color": borderColor,
                        "border-width": borderWidth
                    }
                }, {
                    "selector": "node.focus",
                    "style": {
                        "font-weight": "bold"
                    }
                }, {
                    "selector": "node:selected",
                    "style": {
                        "border-width": selectedBorderWidth,
                        "border-color": borderSelectedColor
                    }
                }, {
                    "selector": "node.hover",
                    "style": {
                        "border-width": hoverBorderWidth,
                        "border-color": borderHighlightColor
                    }
                }, {
                    "selector": "edge",
                    "style": {
                        "line-color": lineColor,
                        "border-width": borderWidth
                    }
                }, {
                    "selector": "edge:selected",
                    "style": {
                        "width": selectedBorderWidth,
                        "line-color": selectedLineColor
                    }
                }, {
                    "selector": "edge.hover",
                    "style": {
                        "width": hoverBorderWidth,
                        "line-color": selectedLineColor
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
                    var viz = self.viz();
                    if (viz) {
                        var element = viz.getElementById(resourceId);
                        if (element) self.informationElement(element.data());
                    }

                    self.selection(null);
                    getResourceRelations(resourceId)
                        .then(function(response) {
                            return response.json();
                        })
                        .then(function(result) {
                            var i = 0;
                            var lookup = result['node_config_lookup'];
                            for (var resourceId in lookup) {
                                lookup[resourceId].className = 'resource-type-' + i;
                                i++;
                            }
                            // add lookup for referencing a missing related resources
                            lookup['undefined'] = {
                                'fillColor': '#CCCCCC'
                            };
                            resourceTypeLookup = lookup;
                            result.resource_instance.focus = true;
                            result.resource_instance['total_relations'] = {
                                value: result.resource_relationships.length
                            };
                            var elements = [dataToElement(result.resource_instance)]
                                .concat(
                                    result.related_resources.concat(result.resource_relationships)
                                        .map(dataToElement)
                                );
                            elements = self.addMissingNodes(elements);
                            self.selection(elements[0].data);
                            if (!viz) {
                                updateCytoscapeConfig(elements);
                            } else {
                                viz.remove('*');
                                viz.add(elements);
                                viz.style(getStyle());
                                viz.layout(layout).run();
                            }
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
                    viz.on('mouseover', 'node, edge', function(e) {
                        self.hoverElementId(e.target.id());
                    });
                    viz.on('mouseout', 'node, edge', function() {
                        self.hoverElementId(null);
                    });
                }
            });

            this.hoverElementId.subscribe(function(elementId) {
                var viz = self.viz();
                if (viz) {
                    viz.elements().removeClass('hover');
                    if (elementId) viz.getElementById(elementId).addClass('hover');
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
                    break;
                case 'focus':
                    if (selection.source) viz.elements().unselect();
                    else self.focusResourceId(selection.id);
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
