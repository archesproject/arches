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
            var values = [];

            $element.ajaxChosen(
                options.ajaxOptions,
                options.ajaxChosenOptions,
                options.chosenOptions
            );


            var keys = ['geocodeTarget'];
            keys.forEach(function(key) {
                var value = options[key];
                if (ko.isObservable(value)) {
                    values.push(value);
                    options[key] = value();
                }
            });

            $element.on('change', function(a) {
                var coords = a.target.value.split(",");
                var numericCoords = _.map(coords, function(coord) {
                    return Number(coord)
                })
                values.forEach(function(value, i) {
                    value(numericCoords);
                })
            });

        }
    };

    return ko.bindingHandlers.ajaxchosen;
});
