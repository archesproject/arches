define(['jquery', 'knockout', 'select2'], function ($, ko) {
    ko.bindingHandlers.select2 = {
        init: function(el, valueAccessor, allBindingsAccessor, viewModel) {
          ko.utils.domNodeDisposal.addDisposeCallback(el, function() {
            $(el).select2('destroy');
          });

          var allBindings = allBindingsAccessor(),
              select2Config = ko.utils.unwrapObservable(allBindings.select2);

          if (select2Config.viewModel && select2Config.conceptKey) {
            select2Config.formatResult = function (item) {
                return item.value;
            };

            select2Config.formatSelection = function (item) {
                select2Config.viewModel[select2Config.conceptKey + '__label'](item.value)
                select2Config.viewModel[select2Config.conceptKey + '__value'](item.id)
                return item.value;
            };
          }

          $(el).select2(select2Config);
        },
        update: function (el, valueAccessor, allBindingsAccessor, viewModel) {
            var allBindings = allBindingsAccessor(),
                select2Config = ko.utils.unwrapObservable(allBindings.select2);

            if ("value" in allBindings) {
                $(el).select2("val", allBindings.value());
            } else if (select2Config.viewModel && select2Config.conceptKey) {
                if ($(el).select2("val") != select2Config.viewModel[select2Config.conceptKey + '__value']()) {
                    $(el).select2("val", select2Config.viewModel[select2Config.conceptKey + '__value']());
                }
            } else if ("selectedOptions" in allBindings) {
                var converted = [];
                var textAccessor = function(value) { return value; };
                if ("optionsText" in allBindings) {
                    textAccessor = function(value) {
                        var valueAccessor = function (item) { return item; }
                        if ("optionsValue" in allBindings) {
                            valueAccessor = function (item) { return item[allBindings.optionsValue]; }
                        }
                        var items = $.grep(allBindings.options(), function (e) { return valueAccessor(e) == value});
                        if (items.length == 0 || items.length > 1) {
                            return "UNKNOWN";
                        }
                        return items[0][allBindings.optionsText];
                    }
                }
                $.each(allBindings.selectedOptions(), function (key, value) {
                    converted.push({id: value, text: textAccessor(value)});
                });
                $(el).select2("data", converted);
            }
        }
    };

    return ko.bindingHandlers.select2;
});