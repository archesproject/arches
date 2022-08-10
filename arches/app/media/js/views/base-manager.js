define([
    'jquery',
    'underscore',
    'knockout',
    'views/page-view',
    'view-data',
    'uuid',
    'core-js',
    'dom-4',
    'views/components/language-switcher'
], function($, _, ko, PageView, data) {
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
        constructor: function(options) {
            options = options ? options : {};
            options.viewModel = (options && options.viewModel) ? options.viewModel : {};

            data.graphs.sort(function(left, right) {
                return left.name.toLowerCase() == right.name.toLowerCase() ? 0 : (left.name.toLowerCase() < right.name.toLowerCase() ? -1 : 1);
            });
            data.graphs.forEach(function(graph){
                graph.name = ko.observable(graph.name);
                graph.iconclass = ko.observable(graph.iconclass);
            });
            options.viewModel.allGraphs = ko.observableArray(data.graphs);
            options.viewModel.graphs = ko.computed(function() {
                return ko.utils.arrayFilter(options.viewModel.allGraphs(), function(graph) {
                    return !graph.isresource;
                });
            });
            options.viewModel.resources = ko.computed(function() {
                return  ko.utils.arrayFilter(options.viewModel.allGraphs(), function(graph) {
                    return graph.isresource;
                });
            });
            options.viewModel.createableResources = ko.observableArray(data.createableResources);
            options.viewModel.userCanReadResources = data.userCanReadResources;
            options.viewModel.userCanEditResources = data.userCanEditResources;

            options.viewModel.setResourceOptionDisable = function(option, item) {
                if (item) {
                    ko.applyBindingsToNode(option, {disable: item.disable_instance_creation}, item);
                }
            };

            options.viewModel.navExpanded = ko.observable(false);
            options.viewModel.inSearch = ko.pureComputed(function() {
                return window.location.pathname === "/search" || window.location.pathname === "/plugins/c8261a41-a409-4e45-b049-c925c28a57da";
            });

            var getHiddenOffsetWidth = function(hiddenElement) {
                var width = 0;
                hiddenElement.style.display = "block";
                hiddenElement.style.position = "absolute";
                width = hiddenElement.offsetWidth;
                hiddenElement.removeAttribute('style');
                return width;
            };

            // this is used to manage the popover menu for the unexpanded side nav 
            let listeles = document.querySelectorAll('div.sidenav-menu > ul > li');
            listeles.forEach(function(listele){
                let menutitle = listele.querySelector('.menu-title');
                if(menutitle){
                    let width = getHiddenOffsetWidth(menutitle);
                    let ulele = listele.querySelector('ul');
                    if(ulele){
                        ulele.style.minWidth = (width + 40) + "px";
                    }
                }
            });

            PageView.prototype.constructor.call(this, options);
            return this;
        }
    });
    
    return BaseManager;
});
