define([
    'jquery',
    'knockout',
    'bootstrap-colorpicker'
], function($, ko, colorpicker) {
    ko.bindingHandlers.colorPicker = {
        init: function(element, valueAccessor) {
            var options = ko.unwrap(valueAccessor());
            var values = [];
            var picking = false;
            var updateValues = function(val) {
                if (!picking) {
                    $(cp).colorpicker('setValue', val)
                }
            };

            var keys = ['color','format'];
            keys.forEach(function(key) {
                var value = options[key];
                if (ko.isObservable(value)) {
                    value.subscribe(updateValues);
                    values.push(value);
                    options[key] = value();
                }
            });

            var cp = $(element).colorpicker(options);

            cp.on('changeColor', function(newValues, options) {
                picking = true;
                values.forEach(function(value, i) {
                    if (newValues.color === undefined) {
                        value(options.color);
                    } else {
                        value(newValues.color.toString());
                    }
                });
                picking = false;
            });
        }
    };
    return ko.bindingHandlers.colorPicker;
});
