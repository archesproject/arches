import ko from 'knockout';
import numeral from 'numeral';

ko.bindingHandlers.formattedNumber = {
    init: function (element, valueAccessor, allBindings) {
        var value = valueAccessor();
        var format = allBindings.get('format');
        var formattedNumber = ko.computed({
            read: function () {
                return numeral(ko.unwrap(value)).format(ko.unwrap(format));
            },
            write: function (newValue) {
                value(numeral(newValue).value());
            }
        }).extend({ notify: 'always' });
        if (element.tagName.toLowerCase() == 'input')
            ko.applyBindingsToNode(element, {
                value: formattedNumber
            });
        else
            ko.applyBindingsToNode(element, {
                text: formattedNumber
            });
    }
};
ko.bindingHandlers.formattedNumber.init = ko.bindingHandlers.formattedNumber.init.bind(ko.bindingHandlers.formattedNumber);

export default ko.bindingHandlers.formattedNumber;
