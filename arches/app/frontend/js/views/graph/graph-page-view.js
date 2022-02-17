define([
    'knockout',
    'underscore',
    'views/base-manager',
    'arches',
    'graph-base-data',
    'bindings/chosen'
], function(ko, _, BaseManager, arches, data) {
    /**
    * A backbone view representing a page in the graph manager workflow.  It
    * adds some graph manager specfic values to the view model.
    *
    * @augments BaseManager
    * @constructor
    * @name GraphPageView
    */
    var GraphPageView = BaseManager.extend({
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
            options.viewModel.graphid = ko.observable(data.graphid);
            BaseManager.apply(this, arguments);
            options.viewModel.graphid.subscribe(function (graphid) {
                var re = /\b[a-f\d-]{36}\b/
                var newPath = window.location.pathname.replace(re, graphid);
                self.viewModel.navigate(newPath);
            });
            return this;
        }
    });
    return GraphPageView;
});
