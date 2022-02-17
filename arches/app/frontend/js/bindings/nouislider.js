define([
    'jquery',
    'knockout',
    'noUiSlider'
], function($, ko, noUiSlider) {
    ko.bindingHandlers.noUiSlider = {
        init: function(element, valueAccessor) {
            var options = ko.unwrap(valueAccessor());
            var values = [];
            var sliding = false;
            var updateValues = function() {
                if (!sliding) {
                    slider.set(values.map(function(value) {
                        return value();
                    }));
                }
            };

            var keys = ['start', 'end'];
            keys.forEach(function (key) {
                var value = options[key];
                if (ko.isObservable(value)) {
                    value.subscribe(updateValues);
                    values.push(value);
                    options[key] = value();
                }
            });

            var slider = noUiSlider.create(element, options);

            element.noUiSlider.on('slide', function(newValues) {
                sliding = true;
                values.forEach(function (value, i) {
                    value(newValues[i]);
                });
                sliding = false;
            });
        }
    };
    return ko.bindingHandlers.noUiSlider;
});
