define([
    'jquery',
    'underscore',
    'knockout',
    'summernote'
], function ($, _, ko) {
    /**
    * A knockout.js binding for the "summernote" rich text editor widget
    * - pass options to summernote using the following syntax in the knockout
    * data-bind attribute
    * @example
    * summernote: {height: 250}
    * @constructor
    * @name summernote
    */
    ko.bindingHandlers.summernote = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
            var $element = $(element);
            var options = ko.unwrap(valueAccessor());
            options = (typeof options === 'object') ? options : {};
            options = _.defaults(options, {
                height: 150,
                value: ko.observable('')
            });

            options.callbacks = options.callbacks ? options.callbacks : {};
            var userChange = options.callbacks.onChange ? options.callbacks.onChange : null;
            options.callbacks.onChange = function(value) {
                if (ko.isObservable(options.value)) {
                    options.value(value);
                } else {
                    options.value = value;
                }
                if (userChange && typeof userChange === 'function') {
                    userChange.apply($element, arguments);
                }
            };

            $element.summernote(options);

            function clearScriptTags(){
                var noteCodable = $('textarea.note-codable')
                noteCodable.val(noteCodable.val().replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, ''))
                console.log('Script tags are not permitted in the code editor')
            }

            $('.btn-codeview').on( "mousedown", clearScriptTags)
            $('textarea.note-codable').on( "keypress", clearScriptTags)

            if (ko.isObservable(options.value)) {
                options.value.subscribe(function(value) {
                    var currentContent = $element.summernote('code');
                    if (value !== currentContent) {
                        $element.summernote('code', value);
                    }
                });
                $element.summernote('code', options.value());
            } else {
                $element.summernote('code', options.value);
            }
        }
    };

    return ko.bindingHandlers.summernote;
});
