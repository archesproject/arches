import ko from 'knockout';

/**
 * A knockout.js binding to alias a given context 
 * Should be available in knockout 3.5 
 * https://github.com/knockout/knockout/pull/1792
 * 
 * Usage:
 *   <!--ko let: { $viewModel: $data }-->
 *   ...
 *   <!--/ko-->
 */

ko.bindingHandlers['let'] = {
    init: function (element, valueAccessor, allBindings, vm, bindingContext) {
        // Make a modified binding context, with extra properties, and apply it to descendant elements
        var innerContext = bindingContext.extend(valueAccessor);
        ko.applyBindingsToDescendants(innerContext, element);

        return { controlsDescendantBindings: true };
    }
};
ko.bindingHandlers['let'].init = ko.bindingHandlers['let'].init.bind(ko.bindingHandlers['let']);

ko.virtualElements.allowedBindings['let'] = true;

export default ko.bindingHandlers['let'];
