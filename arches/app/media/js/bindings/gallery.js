define([
    'jquery',
    'knockout',
], function($, ko) {
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
    return ko.bindingHandlers.gallery;
});
