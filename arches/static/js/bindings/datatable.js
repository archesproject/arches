define([
    'jquery',
    'knockout',
    'datatables.net-responsive-bs'
], function($, ko, DataTable) {
    ko.bindingHandlers.datatable = {
        init: function(element, valueAccessor) {
            var config = ko.unwrap(valueAccessor());
            $(element).DataTable(config);
        }
    };

    ko.bindingHandlers.dataTablesForEach = {
        page: 0,
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var options = ko.unwrap(valueAccessor());
            ko.unwrap(options.data);
            if (options.dataTableOptions.paging) {
                valueAccessor().data.subscribe(function(changes) {
                    var table = $(element).closest('table').DataTable();
                    ko.bindingHandlers.dataTablesForEach.page = table.page();
                    table.destroy();
                }, null, 'arrayChange');
            }
            var nodes = Array.prototype.slice.call(element.childNodes, 0);
            ko.utils.arrayForEach(nodes, function(node) {
                if (node && node.nodeType !== 1) {
                    node.parentNode.removeChild(node);
                }
            });
            return ko.bindingHandlers.foreach.init(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext);
        },
        update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var options = ko.unwrap(valueAccessor()),
                key = 'DataTablesForEach_Initialized';
            ko.unwrap(options.data);
            var table;
            if (!options.dataTableOptions.paging) {
                table = $(element).closest('table').DataTable();
                table.destroy();
            }
            ko.bindingHandlers.foreach.update(element, valueAccessor, allBindings, viewModel, bindingContext);
            table = $(element).closest('table').DataTable(options.dataTableOptions);
            if (options.dataTableOptions.paging) {
                if (table.page.info().pages - ko.bindingHandlers.dataTablesForEach.page == 0)
                    table.page(--ko.bindingHandlers.dataTablesForEach.page).draw(false);
                else
                    table.page(ko.bindingHandlers.dataTablesForEach.page).draw(false);
            }
            if (!ko.utils.domData.get(element, key) && (options.data || options.length))
                ko.utils.domData.set(element, key, true);
            return {
                controlsDescendantBindings: true
            };
        }
    };

    return ko.bindingHandlers.datatable;
});
