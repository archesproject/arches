import ko from 'knockout';
import $ from 'jquery';

ko.bindingHandlers.gallery = {
    init: function() {
        this.initted = true;
    },
    update: function(element, valueAccessor, allBindingsAccessor) {
        var value = valueAccessor();
        var bindings = allBindingsAccessor();
        var pan = value;
        var duration = bindings.duration;
        var thumbnailclass = "." + bindings.thumbnailclass;
        var gt = $(element).find(thumbnailclass)[0];
        pan.subscribe(function(val){
            if (val === 'right') {
                $(gt).animate({scrollLeft: '+=' + $(gt).width()}, duration);
            } else if (val === 'left') {
                $(gt).animate({scrollLeft: '-=' + $(gt).width()}, duration);
            }
        });
        this.initted = false;
    }
};
ko.bindingHandlers.gallery.init = ko.bindingHandlers.gallery.init.bind(ko.bindingHandlers.gallery);
ko.bindingHandlers.gallery.update = ko.bindingHandlers.gallery.update.bind(ko.bindingHandlers.gallery);

export default ko.bindingHandlers.gallery;

