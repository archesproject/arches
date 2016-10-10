define([
    'jquery',
    'knockout',
    'datatables'
], function ($, ko, DataTable) {
    ko.bindingHandlers.datatable = {
        init: function(element, valueAccessor){
            var $element = $(element);
            var config = ko.unwrap(valueAccessor);
            $(element).DataTable(config);
        }
    };

    return ko.bindingHandlers.datatable;
});
