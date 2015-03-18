define(['jquery', 'knockout'], function ($, ko) {
    ko.bindingHandlers.summernote = {
        init: function(el, valueAccessor, allBindings, viewModel, bindingContext) {
            var defaults = {};
            var settings = ko.unwrap(valueAccessor());
            
            defaults.toolbar = [
                ['style', ['bold', 'italic', 'underline', 'clear']], 
                ['fontsize', ['fontsize']], 
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['height', ['height']]
            ];
            defaults.height = 180;
            defaults.focus = false;
            defaults.tabsize = 2;

            defaults.onblur = function() {
                return valueAccessor().value($(el).code());
            };            

            defaults = _.extend(defaults, settings.options);
            
            return $(el).summernote(defaults);
        },

        update: function(el, valueAccessor, allBindings, bindingContext) {
            return $(el).code(ko.utils.unwrapObservable(valueAccessor().value()));
        }
    };

    return ko.bindingHandlers.summernote;
});
