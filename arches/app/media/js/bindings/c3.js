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
            this.chart = c3.generate(options);
            config.data.subscribe(function(val){
                this.chart.load({columns: val});
            }, this);
        },
    };
    return ko.bindingHandlers.c3;
});
