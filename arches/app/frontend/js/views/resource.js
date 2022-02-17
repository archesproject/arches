require([
    'jquery',
    'underscore',
    'knockout',
    'uuid',
    'arches',
    'views/base-manager',
    'bindings/chosen'
], function($, _, ko, uuid, arches, BaseManagerView) {
    /**
    * a BaseManagerView representing the resource listing and recent edits pages
    */
    var ResourceView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;

            _.defaults(this.viewModel, {
                showFind: ko.observable(false),
                graphId: ko.observable(null),
                arches: arches,
            });

            this.viewModel.graphId.subscribe(function(graphid) {
                if(graphid && graphid !== ""){
                    self.viewModel.navigate(arches.urls.add_resource(graphid));
                }
            });

            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new ResourceView();
});
