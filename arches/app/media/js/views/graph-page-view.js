define([
    'knockout',
    'underscore',
    'views/page-view',
    'arches',
    'graph-base-data',
    'bindings/chosen'
], function(ko, _, PageView, arches, data) {
    /**
    * A backbone view representing a page in the graph manager workflow.  It
    * adds some graph manager specfic values to the view model.
    *
    * @augments PageView
    * @constructor
    * @name GraphPageView
    */
    var GraphPageView = PageView.extend({
        /**
        * Creates an instance of GraphPageView, optionally using a passed in
        * view model
        *
        * @memberof GraphPageView.prototype
        * @param {object} options
        * @param {object} options.viewModel - an optional view model to be
        *                 bound to the page
        * @return {object} an instance of GraphPageView
        */
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
