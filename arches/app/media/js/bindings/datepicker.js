define([
    'jquery',
    'underscore',
    'knockout',
    'moment',
    'bootstrap-datetimepicker',
], function($, _, ko, moment) {
    /**
    * A knockout.js binding for the jQuery UI datepicker
    * @constructor
    * @name datepicker
    */
    ko.bindingHandlers.datepicker = {
        init: function(element, valueAccessor, allBindingsAccessor) {
            //initialize datepicker with some optional options
            var options = valueAccessor() || {};
            var minDate;
            var maxDate;

            _.forEach(options, function(value, key){
                if (ko.isObservable(value)) {
                    var rawValue = options[key]();
                    if (key === 'minDate') {
                        minDate = value;
                        rawValue = rawValue || false;
                    } else if (key === 'maxDate') {
                        maxDate = value;
                        rawValue = rawValue || false;
                    }

                    value.subscribe(function(newValue) {
                        if (_.isObject(newValue)) {
                            newValue = moment(newValue).format(options['format']);
                        }
                        options[key] = newValue || false;

                        if ((key === 'minDate' || key === 'maxDate') &&
                            typeof minDate === 'function' && minDate() &&
                            typeof maxDate === 'function' && maxDate() &&
                            (minDate() > maxDate() || maxDate() < minDate())) {
                            if (key === 'minDate' && maxDate()) {
                                maxDate(minDate());
                            } else if (minDate()) {
                                minDate(maxDate());
                            }
                            options[key === 'minDate' ? 'maxDate': 'minDate'] = moment(newValue).format(options['format']).toDate();
                        }

                        var picker = $(element).data("DateTimePicker");
                        _.each(options, function(val, key) {
                            if (!val) {
                                delete options[key];
                            }
                        });
                        if (picker) {
                            picker.options(options);
                            picker.date(allBindingsAccessor().value());
                        }
                    });

                    options[key] = rawValue;
                }
            });

            _.each(options, function(val, key) {
                if (!val) {
                    delete options[key];
                }
            });

            var format = options.format;
            if (!!options['keepInvalid']) {
                delete options['format'];
            }

            $(element).datetimepicker(options);

            var value = allBindingsAccessor().value;
            var picker = $(element).data("DateTimePicker");
            value.subscribe(val=> {
                if (val !== 'Date of Data Entry'){
                    picker.date(val);
                }
            });

            ko.utils.registerEventHandler(element, "dp.change", function(event) {
                if (ko.isObservable(value)) {
                    if (value() === "" || event.date === false) {
                        value(null);
                    }else if (event.date.isValid()) {
                        value(event.date.format(format));
                    }
                }
            });

            ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
                var picker = $(element).data("datepicker");
                if (picker) {
                    picker.destroy();
                }
            });
        }
    };

    return ko.bindingHandlers.datepicker;
});
