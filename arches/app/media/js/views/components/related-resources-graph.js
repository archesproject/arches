define([
    'arches',
    'knockout',
    'views/components/workbench',
    'bindings/cytoscape'
], function(arches, ko, WorkbenchViewmodel) {
    return ko.components.register('related-resources-graph', {
        viewModel: function(params) {
            var self = this;

            this.viz = ko.observable();
            this.cytoscapeConfig = ko.observable();
            this.focusResourceId = ko.observable(params.resourceId);

            WorkbenchViewmodel.apply(this, [params]);

            var updateCytoscapeConfig = function(elements) {
                self.cytoscapeConfig({
                    elements: elements,
                    layout: {
                        name:'random'
                    }
                });
            };
            var getResourceRelations = function(resourceId) {
                var url = arches.urls.related_resources + resourceId + '?paginate=false';
                return window.fetch(url);
            };
            var dataToElement = function(data) {
                data.id = data.resourceinstanceid;
                data.source = data.resourceinstanceidfrom;
                data.target = data.resourceinstanceidto;
                return {
                    data: data
                };
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
                            result.resource_instance.focus = true;
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
                if (!viz) self.cytoscapeConfig(null);
            });

            updateFocusResource();
        },
        template: { require: 'text!templates/views/components/related-resources-graph.htm' }
    });
});
