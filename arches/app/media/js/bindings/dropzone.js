define([
    'jquery',
    'knockout',
    'dropzone'
], function($, ko, dropzone) {
    /**
     * @constructor
     * @name dropzone
     */
    ko.bindingHandlers.dropzone = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            options = valueAccessor() || {};

            _.each(_.filter(options, function (value, key) {
                    return _.contains(['previewsContainer', 'clickable'], key)
                }),function(value, key) {
                    options[key] = $(element).find(value)[0];
                });

            var optionsInit = options.init;
            var dropzoneInit = function() {
                this.on('success', function(file, resp) {
                    if (Array.isArray(options.value()))
                        options.value.push(resp.url);
                    else
                        options.value(resp.url);
                });

                this.on('error', function(file, err) {
                    console.error('dropzone@err:', err);
                });

                this.on('removedfile', function(file) {
                    var imageUrl = JSON.parse(file.xhr.response).url;
                    if (Array.isArray(options.value())) {
                        options.value.remove(imageUrl);
                    } else {
                        options.value(null);
                    }
                });

                if (typeof optionsInit === 'function') {
                    optionsInit.apply(this);
                }
            };

            $.extend(options, {
                init: dropzoneInit
            });

            $(element).dropzone(options);
        }
    }
    return ko.bindingHandlers.dropzone;
});
