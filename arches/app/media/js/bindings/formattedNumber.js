define([
    'jquery',
    'knockout',
    'numeral'
], function($, ko, numeral) {
    ko.bindingHandlers.formattedNumber = {
        init: function(element, valueAccessor, allBindings) {
            var value = valueAccessor();
            var format = allBindings.get('format');
            var formattedNumber = ko.computed({
                read: function() {
                    return numeral(ko.unwrap(value)).format(ko.unwrap(format));
                },
                write: function(newValue) {
                    value(numeral(newValue).value());
                }
            }).extend({notify: 'always'});
            if(element.tagName.toLowerCase() == 'input' )
                ko.applyBindingsToNode(element, {
                    value: formattedNumber
                });
            else
                ko.applyBindingsToNode(element, {
                    text: formattedNumber
                });
        }
    };
    return ko.bindingHandlers.formattedNumber;
});
