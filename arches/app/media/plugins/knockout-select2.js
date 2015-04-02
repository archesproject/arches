
define(['jquery', 'knockout', 'underscore', 'select2'], function ($, ko, _) {
    ko.bindingHandlers.select2 = {
        init: function(el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var self = this;
            var data;
            var domains = {};
            var allBindings = allBindingsAccessor();
            var branchList = bindingContext.$data;
            var select2Config = ko.utils.unwrapObservable(allBindings.select2);            

            ko.utils.domNodeDisposal.addDisposeCallback(el, function() {
                $(el).select2('destroy');
            });

            select2Config.formatResult = function (item) {
                return item.value;
            };

            select2Config.formatSelection = function (item) {
                return item.value;
            };

            domains[select2Config.dataKey] = [];
            domains = select2Config.domains || branchList.domains || (branchList.viewModel ? branchList.viewModel.domains : undefined) || domains;
            data = domains[select2Config.dataKey];

            select2Config.data = _.filter(data, function (item) {
                return (item.valuetype === "collector") ? (item.children.length > 0) : true;
            });

            _.each(select2Config.data, function (item) {
                if (item.valuetype === "collector") {
                    delete item.id;
                }
            });

            $(el).select2(select2Config);

            $(el).on("change", function(val) {
                if(val.added){
                    return select2Config.value({'value':val.added.id, 'label':val.added.value, 'entitytypeid': val.added.entitytypeid});
                }
                return select2Config.value(val.val);
            });
        },
        update: function (el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var val = ko.utils.unwrapObservable(valueAccessor().value());
            if (typeof val === 'string' || val === null){
                return $(el).select2("val", val, true);
            }
            if (typeof val === 'object'){
                return $(el).select2("val", val.value, true);
            }
            
        }
    };

    return ko.bindingHandlers.select2;
});