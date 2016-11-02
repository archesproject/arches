define([
    'jquery',
    'knockout',
    'underscore',
    'dropzone',
    'viewmodels/widget',
    'bindings/dropzone'
], function($, ko, _, Dropzone, WidgetViewModel) {
    /**
     * registers a text-widget component for use in forms
     * @function external:"ko.components".text-widget
     * @param {object} params
     * @param {string} params.value - the value being managed
     * @param {function} params.config - observable containing config object
     * @param {string} params.config().instructions - label to use alongside the text input
     */
    return ko.components.register('file-widget', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = [];

            WidgetViewModel.apply(this, [params]);
            
            this.dropzoneButtonsDisabled = ko.observable(true);
            this.showProgressBar = ko.observable(false);
            this.progress = ko.observable(0);
            
            this.dropzoneOptions = { 
                value: this.value,
                url: "/target-url",
                autoProcessQueue: false,
                thumbnailWidth: 50,
                thumbnailHeight: 50,
                parallelUploads: 20,
                previewTemplate: $("template#file-widget-dz-preview").html(),
                autoQueue: false,
                previewsContainer: ".dz-previews",
                clickable: ".fileinput-button",
                init: function () {
                    self.dropzone = this;
                    
                    this.on("addedfile", function(file) {
                        self.dropzoneButtonsDisabled(false);
                    });
                    
                    this.on("totaluploadprogress", function(progress) {
                        self.progress(progress);
                    });
                    
                    this.on("sending", function(file) {
                        self.showProgressBar(true);
                    });
                    
                    this.on("queuecomplete", function(progress) {
                        self.progress(0);
                        self.showProgressBar(false);
                    });
                }
            };
            
            this.uploadFiles = function() {
                if (self.dropzone) {
                    self.dropzone.enqueueFiles(self.dropzone.getQueuedFiles());
                }
            };
            
            this.reset = function() {
                if (self.dropzone) {
                    self.dropzone.removeAllFiles(true);
                    self.dropzoneButtonsDisabled(true);
                }
            };
        },
        template: {
            require: 'text!widget-templates/file'
        }
    });
});
