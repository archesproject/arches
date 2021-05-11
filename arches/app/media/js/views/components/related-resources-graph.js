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
                name: "random"
            };

            this.viz = ko.observable();
            this.cytoscapeConfig = ko.observable();
            this.focusResourceId = ko.isObservable(params.resourceId) ? params.resourceId : ko.observable(params.resourceId);
            this.selection = ko.observable();

            WorkbenchViewmodel.apply(this, [params]);

            var getResourceRelations = function(resourceId) {
                var url = arches.urls.related_resources + resourceId + '?paginate=false';
                return window.fetch(url);
            };
            var resourceTypeLookup = {};
            var dataToElement = function(data) {
                data.id = data.resourceinstanceid;
                data.source = data.resourceinstanceidfrom;
                data.target = data.resourceinstanceidto;
                var classes = [];
                if (data.graph_id) classes.push(resourceTypeLookup[data.graph_id].className);
                if (data.focus) classes.push('focus');
                return {
                    data: data,
                    classes: classes,
                    selected: data.focus
                };
            };
            var getStyle = function() {
                var styles = [{
                    "selector": "node",
                    "style": {
                        "content": "data(displayname)",
                        "font-size": "12px",
                        "text-valign": "center",
                        "text-halign": "center",
                        "border-color": "black",
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
                        "border-width": 3
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
                            self.selection(result.resource_instance);
                            var elements = [dataToElement(result.resource_instance)]
                                .concat(
                                    result.related_resources.concat(result.resource_relationships)
                                        .map(dataToElement)
                                );
                            updateCytoscapeConfig(elements);
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

            updateFocusResource();
        },
        template: { require: 'text!templates/views/components/related-resources-graph.htm' }
    });
});
