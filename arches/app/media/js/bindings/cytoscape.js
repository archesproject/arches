define([
    'knockout',
    'underscore',
    'cytoscape'
], function(ko, _, cytoscape) {
    ko.bindingHandlers.cytoscape = {
        init: function(element, valueAccessor) {
            var defaults = {
                container: element
            };
            var config = ko.unwrap(valueAccessor()).config || {};

            var viz = cytoscape(
                _.defaults(config, defaults)
            );

            ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
                viz.destroy();
            }, this);

            if (typeof ko.unwrap(valueAccessor()).afterRender === 'function') {
                ko.unwrap(valueAccessor()).afterRender(viz);
            }
        },
    };
    return ko.bindingHandlers.cytoscape;
});
