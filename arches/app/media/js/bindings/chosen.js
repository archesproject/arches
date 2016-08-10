define([
    'jquery',
    'underscore',
    'knockout',
    'chosen'
], function ($, _, ko) {
    /**
    * A knockout.js binding for the "chosen.js" select box - https://harvesthq.github.io/chosen/
    * - pass options to chosen using the following syntax in the knockout data-bind attribute
    * @example
    * chosen: {disable_search_threshold: 10, width: '100%', ....}"
    * @constructor
    * @name chosen
    */
    ko.bindingHandlers.chosen = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
            var $element = $(element);
            var options = ko.unwrap(valueAccessor());
            var defaults = {
                search_contains: true
            };

            if (typeof options === 'object')
                $element.chosen(_.defaults(options, defaults));
            else
                $element.chosen(defaults);

            ['options', 'selectedOptions', 'value'].forEach(function(propName){
                if (allBindings.has(propName)){
                    var prop = allBindings.get(propName);
                    if (ko.isObservable(prop)){
                        prop.subscribe(function(){
                            $element.trigger('chosen:updated');
                        });
                    }
                }
            });
        }
    };

    return ko.bindingHandlers.chosen;
});
