define([
    'knockout',
    'views/components/workbench',
    'bindings/cytoscape'
], function(ko, WorkbenchViewmodel) {
    return ko.components.register('related-resources-graph', {
        viewModel: function(params) {
            this.viz = ko.observable();
            this.cytoscapeConfig = {

            };
            this.viz.subscribe(function(viz) {
                console.log(viz);
            });
            WorkbenchViewmodel.apply(this, [params]);
        },
        template: { require: 'text!templates/views/components/related-resources-graph.htm' }
    });
});
