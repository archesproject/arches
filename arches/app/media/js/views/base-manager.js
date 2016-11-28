define([
    'jquery',
    'underscore',
    'knockout',
    'backbone',
    'views/page-view',
    'view-data'
], function($, _, ko, Backbone, PageView, data) {

    var BaseManager = PageView.extend({
        /**
        * Creates an instance of PageView, optionally using a passed in view model
        * appends the following properties to viewModel:
        * allGraphs - an array of graphs models as JSON (not model instances)
        *
        * @memberof PageView.prototype
        * @param {object} options
        * @param {object} options.viewModel - an optional view model to be
        *                 bound to the page
        * @return {object} an instance of BaseManager
        */
        constructor: function (options) {
            options = options ? options : {};
            options.viewModel = (options && options.viewModel) ? options.viewModel : {};

            data.graphs.sort(function (left, right) {
                return left.name.toLowerCase() == right.name.toLowerCase() ? 0 : (left.name.toLowerCase() < right.name.toLowerCase() ? -1 : 1);
            });
            options.viewModel.allGraphs = ko.observableArray(data.graphs);
            options.viewModel.graphs = ko.computed(function() {
                return ko.utils.arrayFilter(options.viewModel.allGraphs(), function(graph) {
                    return !graph.isresource;
                });
            });
            options.viewModel.resources = ko.computed(function() {
                var resources =  ko.utils.arrayFilter(options.viewModel.allGraphs(), function(graph) {
                    graph.disable = true;
                    return graph.isresource;
                });
                console.log(resources);
                return resources;
            });

            options.viewModel.setResourceOptionDisable = function(option, item) {
              if (item) {
                ko.applyBindingsToNode(option, {disable: !item.isactive || !item.forms}, item);
              }
            };

            PageView.prototype.constructor.call(this, options);
            return this;
        }

    });
    return BaseManager;


});
