define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'chosen',
    'plugins/chosen.ajaxaddition.jquery'
], function($, _, ko, arc, chosen, chosenajax) {
    /**
     * A knockout.js binding for the "chosen.js" select box - https://harvesthq.github.io/chosen/
     * - pass options to chosen using the following syntax in the knockout data-bind attribute
     * @example
     * chosen: {disable_search_threshold: 10, width: '100%', ....}"
     * @constructor
     * @name chosen
     */
    ko.bindingHandlers.ajaxchosen = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var $element = $(element);
            var options = ko.unwrap(valueAccessor());

            $element.ajaxChosen(
                options.ajaxOptions,
                options.ajaxChosenOptions,
                options.chosenOptions
            );

            var value = options.value;

            $element.on('change', function(val) {
                value(val.currentTarget.value);
            });

            ['value'].forEach(function(propName){
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

    return ko.bindingHandlers.ajaxchosen;
});
