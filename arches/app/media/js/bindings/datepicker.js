define([
    'jquery',
    'underscore',
    'knockout',
    'moment',
    'bootstrap-datetimepicker',
], function ($, _, ko, moment) {
    /**
    * A knockout.js binding for the jQuery UI datepicker
    * @constructor
    * @name datepicker
    */
    ko.bindingHandlers.datepicker = {
        init: function (element, valueAccessor, allBindingsAccessor) {
            //initialize datepicker with some optional options
            var options = valueAccessor() || {};
            var minDate;
            var maxDate;

            _.forEach(options, function (value, key){
                if (ko.isObservable(value)) {
                    if (key === 'minDate') {
                        minDate = value;
                    } else if (key === 'maxDate') {
                        maxDate = value;
                    }

                    value.subscribe(function (newValue) {
                        if (_.isObject(newValue)) {
                          newValue = moment(newValue).format(options['format']);
                        }
                        options[key] = newValue;

                        if ((key === 'minDate' || key === 'maxDate') &&
                            typeof minDate === 'function' && minDate() &&
                            typeof maxDate === 'function' && maxDate() &&
                            (minDate() > maxDate() || maxDate() < minDate())) {
                            if (key === 'minDate') {
                                maxDate(minDate());
                            } else {
                                minDate(maxDate());
                            }
                            options[key === 'minDate' ? 'maxDate': 'minDate'] = newValue;
                        }

                        var picker = $(element).data("DateTimePicker");
                        if (picker) {
                            picker.options(options);
                            picker.date(allBindingsAccessor().value());
                        }
                    });

                    options[key] = options[key]();
                }
            })

            $(element).datetimepicker(options);

            ko.utils.registerEventHandler(element, "dp.change", function (event) {
                var value = allBindingsAccessor().value;
                var picker = $(element).data("DateTimePicker");
                if (ko.isObservable(value)) {
                    if (event.date) {
                        value(event.date.format(picker.format()));
                    }
                }
            });

            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                var picker = $(element).data("datepicker");
                if (picker) {
                    picker.destroy();
                }
            });
        }
    };

    return ko.bindingHandlers.datepicker;
});
