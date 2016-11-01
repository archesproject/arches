define([
    'knockout',
    'underscore',
    'dropzone',
    'viewmodels/widget',
    'bindings/dropzone'
], function(ko, _, Dropzone, WidgetViewModel) {
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

            this.images = ko.observableArray([]); // Multiple images.

            WidgetViewModel.apply(this, [params]);

            var previewNode = document.querySelector("#file-widget-dz-preview");
            var previewTemplate = previewNode.innerHTML;
            
            this.dropzoneButtonsDisabled = ko.observable(true);
            this.showProgressBar = ko.observable(false);
            this.progress = ko.observable(0);
            
            this.dropzoneOptions = { 
                value: this.images,
                url: "/target-url", // Set the url
                autoProcessQueue: false,
                thumbnailWidth: 50,
                thumbnailHeight: 50,
                parallelUploads: 20,
                previewTemplate: previewTemplate,
                autoQueue: false, // Make sure the files aren't queued until manually added
                previewsContainer: "#dz-previews", // Define the container to display the previews
                clickable: ".fileinput-button", // Define the element that should be used as click trigger to select files.
                init: function () {
                    console.log(this)
                    self.dropzone = this;
                    
                    this.on("addedfile", function(file) {
                        self.dropzoneButtonsDisabled(false);
                    });
                    
                    // Update the total progress bar
                    this.on("totaluploadprogress", function(progress) {
                        // $("#dz-total-progress .progress-bar").css({
                        //     'width': progress + "%"
                        // });
                        self.progress(progress);
                    });
                    
                    this.on("sending", function(file) {
                        self.showProgressBar(true);
                        // document.querySelector("#dz-total-progress").style.opacity = "1";
                    });
                    
                    // Hide the total progress bar when nothing's uploading anymore
                    this.on("queuecomplete", function(progress) {
                        self.progress(0);
                        self.showProgressBar(false);
                        // document.querySelector("#dz-total-progress").style.opacity = "0";
                    });
                    
                }
            };
            
            
            this.uploadFiles = function() {
                if (self.dropzone) {
                    self.dropzone.enqueueFiles(self.dropzone.getFilesWithStatus(Dropzone.ADDED));
                }
            };
            
            this.removeAllFiles = function() {
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
