define([
    'jquery',
    'knockout',
    'c3'
], function($, ko, c3) {
    ko.bindingHandlers.c3 = {
        init: function(element, valueAccessor) {
            var config = ko.unwrap(valueAccessor());
            var options = $.extend(true, config.options, {
                bindto: element,
                data: {
                    x: 'value',
                    columns: ko.unwrap(config.data),
                    keys: {
                        value: ['count'],
                    }
                },
                axis: {
                    x: {
                        tick: {
                            format: function(val) {
                                return Math.floor(val);
                            }
                        }
                    }
                }
            });
            var chart = c3.generate(options);
            config.data.subscribe(function(val){
                chart.load({columns: val});
            }, this);

            // Handle disposal if KO removes an chart through template binding
            ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
                chart.destroy();
            }, this); 
        },
    };
    return ko.bindingHandlers.c3;
});
