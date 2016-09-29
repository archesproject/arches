define([
    'jquery',
    'knockout',
    'noUiSlider'
], function($, ko, noUiSlider) {
    ko.bindingHandlers.noUiSlider = {
        init: function(element, valueAccessor, allBindingsAccesor, viewModel, bindingContext) {
            var options = ko.unwrap(valueAccessor());
            var updateValues = function() {
                var values = [];
                if (start) {
                    values.push(start());
                }
                if (end) {
                    values.push(end());
                }
                slider.set(values)
            }
            var start;
            var end;
            if (ko.isObservable(options.start)) {
                start = options.start;
                options.start = start();
                start.subscribe(updateValues);
            }

            if (ko.isObservable(options.end)) {
                end = options.end;
                options.end = end();
                end.subscribe(updateValues);
            }

            var slider = noUiSlider.create(element, options);

            element.noUiSlider.on('slide', function(values, handle) {
                var value = values[handle];
                if (start) {
                    start(values[0]);
                }
                if (end) {
                    start(values[1]);
                }
            });
        }
    };
    return ko.bindingHandlers.noUiSlider;
});
