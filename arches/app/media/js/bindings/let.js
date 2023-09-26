define([
    'knockout',
], function(ko) {
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
        init: function(element, valueAccessor, allBindings, vm, bindingContext) {
            // Make a modified binding context, with extra properties, and apply it to descendant elements
            var innerContext = bindingContext.extend(valueAccessor);
            ko.applyBindingsToDescendants(innerContext, element);

            return { controlsDescendantBindings: true };
        }
    };

    ko.virtualElements.allowedBindings['let'] = true;

    return ko.bindingHandlers['let'];
});