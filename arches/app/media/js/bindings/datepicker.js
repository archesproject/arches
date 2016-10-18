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
            //initialize datepicker with some optional options
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

            //when a user changes the date, update the view model
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
            //when the view model is updated, update the widget
            if (picker) {
                var koDate = ko.utils.unwrapObservable(valueAccessor());
                if (koDate) {
                  //in case return from server datetime i am get in this form for example /Date(93989393)/ then fomat this
                  koDate = (typeof (koDate) !== 'object') ? new Date(parseFloat(koDate.replace(/[^0-9]/g, ''))) : koDate;
                  koDate = moment(koDate).format(picker.format());
                  picker.date(koDate);
                }
            }
        }
    };

    return ko.bindingHandlers.datepicker;
});
