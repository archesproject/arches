define([
    'jquery',
    'knockout',
    'datatables.net-responsive-bs'
], function ($, ko, DataTable) {
    ko.bindingHandlers.datatable = {
        init: function(element, valueAccessor){
            var config = ko.unwrap(valueAccessor());
            $(element).DataTable(config);
        }
    };

    return ko.bindingHandlers.datatable;
});
