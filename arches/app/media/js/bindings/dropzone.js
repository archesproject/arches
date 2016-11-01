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
            window.test = element;
            options = valueAccessor() || {};

            _.each(_.filter(options, function (value, key) {
                    return _.contains(['previewsContainer', 'clickable'], key)
                }),function(value, key) {
                    options[key] = $(element).find(value)[0];
                });

            var removeImage = function(imageUrl) {
                return $.ajax({
                        url: imageUrl,
                        type: 'DELETE'
                    })
                    .error(function() {
                        console.error('dropzone@err:', err);
                    })
            };

            var optionsInit = options.init;
            var dropzoneInit = function() {
                this.on('success', function(file, resp) {
                    if (Array.isArray(options.value())) // check observableArray
                        options.value.push(resp.url);
                    else
                        options.value(resp.url);
                });

                this.on('error', function(file, err) {
                    console.error('dropzone@err:', err);
                });

                this.on('removedfile', function(file) {
                    if (Array.isArray(options.value())) { // check observableArray
                        var imageUrl = JSON.parse(file.xhr.response).url;
                        removeImage(imageUrl)
                            .done(function(resp) {
                                options.value.remove(imageUrl);
                            })
                    } else {
                        var imageUrl = JSON.parse(file.xhr.response).url;
                        removeImage(imageUrl)
                            .done(function(resp) {
                                options.value('');
                            })
                    }
                });

                if (typeof optionsInit === 'function') {
                    optionsInit.apply(this);
                }
            };

            $.extend(options, {
                acceptedFiles: 'image/*',
                addRemoveLinks: true,
                init: dropzoneInit
            });

            $(element).dropzone(options);
        }
    }
    return ko.bindingHandlers.dropzone;
});
