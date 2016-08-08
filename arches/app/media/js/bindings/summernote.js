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
    * summernote: {height: 250}"
    * @constructor
    * @name summernote
    */
    ko.bindingHandlers.summernote = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
            var $element = $(element);
            var options = ko.unwrap(valueAccessor());
            options = (typeof options === 'object') ? options : {};
            options = _.defaults(options, {
                height: 250,
                value: ko.observable('')
            });

            options.callbacks = {
                onChange: function(value) {
                    if (ko.isObservable(options.value)) {
                        options.value(value);
                    } else {
                        options.value = value;
                    }
                }
            };

            $element.summernote(options);

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
    }

    return ko.bindingHandlers.summernote;
});
