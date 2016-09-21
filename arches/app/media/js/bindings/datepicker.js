define([
    'jquery',
    'knockout',
    'bootstrap-datepicker'
], function ($, ko) {
    /**
    * A knockout.js binding for the jQuery UI datepicker, passes datepickerOptions
    * data-bind property to the datepicker on init
    * @constructor
    * @name datepicker
    */
    ko.bindingHandlers.datepicker = {
        init: function(element, valueAccessor, allBindingsAccessor) {
          //initialize datepicker with some optional options
          var options = allBindingsAccessor().datepickerOptions || { autoclose: true, format: "yyyy-mm-dd"};
          var value = valueAccessor();
          var widget = $(element).datepicker(options).data("datepicker");
          if (typeof value() === 'string') {
              var dateValue = new Date(value());
              value(dateValue);
              widget.setDate(dateValue);
          }

          //when a user changes the date, update the view model
          ko.utils.registerEventHandler(element, "changeDate", function(event) {
                 var value = valueAccessor();
                 if (ko.isObservable(value)) {
                     value(event.date);
                 }
          });
        },
        update: function(element, valueAccessor)   {
            var widget = $(element).data("datepicker");
             //when the view model is updated, update the widget
            if (widget) {
                widget.date = ko.utils.unwrapObservable(valueAccessor());
                widget.setValue();
            }
        }
    };

    return ko.bindingHandlers.datepicker;
});
