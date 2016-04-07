define([
    'jquery',
    'knockout',
    'chosen'
], function ($, ko) {
    ko.bindingHandlers.chosen = {
        init: function(element, valueAccessor, allBindingsAccessor) {
            var options = allBindingsAccessor().chosenOptions || {};
            $(element).addClass('chzn-select');
            $(element).chosen(options);
        },
        update: function(element) {
            $(element).trigger('liszt:updated');
        }
    };


    return ko.bindingHandlers.datepicker;
});
