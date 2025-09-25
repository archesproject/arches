import ko from 'knockout';
import _ from 'underscore';
import cytoscape from 'cytoscape';
import cola from 'cytoscape-cola';

cytoscape.use(cola);

ko.bindingHandlers.cytoscape = {
    init: function (element, valueAccessor) {
        var defaults = {
            container: element
        };
        var config = ko.unwrap(valueAccessor()).config || {};

        var viz = cytoscape(
            _.defaults(ko.unwrap(config), defaults)
        );

        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            viz.destroy();
        }, this);

        if (typeof ko.unwrap(valueAccessor()).afterRender === 'function') {
            ko.unwrap(valueAccessor()).afterRender(viz);
        }
    },
};

ko.bindingHandlers.cytoscape.init = ko.bindingHandlers.cytoscape.init.bind(ko.bindingHandlers.cytoscape);
export default ko.bindingHandlers.cytoscape;
