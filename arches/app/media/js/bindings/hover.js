import ko from 'knockout';

ko.bindingHandlers.hover = {
    init: function(element, valueAccessor) {
        var value = valueAccessor();
        ko.applyBindingsToNode(element, {
            event: {
                mouseenter: function() { value(true); },
                mouseleave: function() { value(false); }
            }
        });
    }
};
ko.bindingHandlers.hover.init = ko.bindingHandlers.hover.init.bind(ko.bindingHandlers.hover);

export default ko.bindingHandlers.hover;
