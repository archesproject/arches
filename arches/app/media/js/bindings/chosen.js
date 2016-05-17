define([
    'jquery',
    'knockout',
    'chosen'
], function ($, ko) {
    ko.bindingHandlers.chosen = {
        init: function(element, valueAccessor, allBindingsAccessor) {
            $(element).addClass('chzn-select');
            $(element).chosen({ width: '100%' });
        },
        update: function(element) {
            $(element).trigger('liszt:updated');
        }
    };


    return ko.bindingHandlers.datepicker;
});
