
define(['jquery', 'knockout', 'underscore', 'select2'], function ($, ko, _) {
    ko.bindingHandlers.select2 = {
        init: function(el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var self = this;
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

            select2Config.data = _.filter(branchList.viewModel.domains[select2Config.dataKey], function (item) {
                return (item.valuetype === "collector") ? (item.children.length > 0) : true;
            });

            _.each(select2Config.data, function (item) {
                if (item.valuetype === "collector") {
                    delete item.id;
                }
            });

            $(el).select2(select2Config);

            $(el).on("change", function(val) {
                console.log(val);
                if(val.added){
                    return select2Config.value({'value':val.added.id, 'label':val.added.value, 'entitytypeid': val.added.entitytypeid});
                }
                return select2Config.value(val.val);
            });
        },
        update: function (el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            return $(el).select2("val", ko.utils.unwrapObservable(valueAccessor().value()), true);
        }
    };

    return ko.bindingHandlers.select2;
});