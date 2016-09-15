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
            _.defaults(options.viewModel, {
                allGraphs: ko.observableArray(data.graphs)
            });
            
            PageView.prototype.constructor.call(this, options);
            return this;
        }

    });
    return BaseManager;


});
