define([
    'jquery',
    'underscore',
    'knockout',
    'moment',
    'bootstrap-datetimepicker',
], function ($, _, ko, moment) {
    /**
    * A knockout.js binding for the jQuery UI datepicker, passes datepickerOptions
    * data-bind property to the datepicker on init
    * @constructor
    * @name datepicker
    */
    ko.bindingHandlers.datepicker = {
        init: function (element, valueAccessor, allBindingsAccessor) {
            var options = allBindingsAccessor().datepickerOptions || {};
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
                        }
                    });

                    options[key] = options[key]();
                }
            })

            $(element).datetimepicker(options);

            ko.utils.registerEventHandler(element, "dp.change", function (event) {
                var value = valueAccessor();
                if (ko.isObservable(value)) {
                    if (event.date != null && !(event.date instanceof Date)) {
                        value(event.date.toDate());
                    } else {
                        value(event.date);
                    }
                }
            });

            ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
                var picker = $(element).data("datepicker");
                if (picker) {
                    picker.destroy();
                }
            });
        },
        update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
            var picker = $(element).data("DateTimePicker");
            if (picker) {
                var koDate = ko.utils.unwrapObservable(valueAccessor());
                console.log('update', koDate);
                if (koDate) {
                  koDate = moment(koDate);
                  picker.date(koDate);
                }
            }
        }
    };

    return ko.bindingHandlers.datepicker;
});
