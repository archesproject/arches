import $ from 'jquery'; 
import ko from 'knockout';

ko.bindingHandlers.slide = {
    init: function() {
        this.initted = true;
    },
    update: function(element, valueAccessor, allBindingsAccessor) {
        var value = valueAccessor();
        var bindings = allBindingsAccessor();
        var direction = bindings.direction;
        var easing = bindings.easing;
        if (value() === true) {
            $(element).toggle(easing, direction);
        }
        else if (this.initted === false && value() === false) {
            $(element).toggle(easing, direction);
        }
        this.initted = false;
    }
};
ko.bindingHandlers.slide.init = ko.bindingHandlers.slide.init.bind(ko.bindingHandlers.slide);
ko.bindingHandlers.slide.update = ko.bindingHandlers.slide.update.bind(ko.bindingHandlers.slide);

export default ko.bindingHandlers.slide;
