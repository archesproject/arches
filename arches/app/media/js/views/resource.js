require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'bindings/chosen'
], function($, _, ko, arches, BaseManagerView) {
    /**
    * a BaseManagerView representing the resource listing and recent edits pages
    */
    var ResourceView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;

            _.defaults(this.viewModel, {
                showFind: ko.observable(false),
                graphId: ko.observable(null)
            });

            this.viewModel.graphId.subscribe(function (graphid) {
                if(graphid && graphid !== ""){
                    self.viewModel.navigate(arches.urls.graph + graphid + '/add_resource');
                }
            });

            BaseManagerView.prototype.initialize.call(this, options)
        }
    });
    return new ResourceView();
});
