define([
    'knockout',
    'underscore',
    'views/page-view',
    'arches',
    'graph-base-data',
    'bindings/chosen'
], function(ko, _, PageView, arches, data) {
    var GraphPageView = PageView.extend({
        constructor: function (options) {
            var self = this;
            options.viewModel.graphs = data.graphs;
            options.viewModel.graphid = ko.observable(data.graphid);
            PageView.apply(this, arguments);
            options.viewModel.graphid.subscribe(function (graphid) {
                self.viewModel.navigate(arches.urls.graph + graphid + '/settings');
            });
            return this;
        }
    });
    return GraphPageView;
});
