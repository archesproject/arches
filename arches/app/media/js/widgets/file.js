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

            params.configKeys = [];

            this.images = ko.observableArray([]); // Multiple images.

            WidgetViewModel.apply(this, [params]);

            if (!this.configForm) {
                var self = this;

                var previewNode = document.querySelector("#dz-template");
                previewNode.id = "";
                var previewTemplate = previewNode.innerHTML;
                previewNode.parentNode.removeChild(previewNode);

                var dropzone = new Dropzone(document.body, { // Make the whole body a dropzone
                    url: "/target-url", // Set the url
                    autoProcessQueue: false,
                    thumbnailWidth: 50,
                    thumbnailHeight: 50,
                    parallelUploads: 20,
                    previewTemplate: previewTemplate,
                    autoQueue: false, // Make sure the files aren't queued until manually added
                    previewsContainer: "#dz-previews", // Define the container to display the previews
                    clickable: ".fileinput-button" // Define the element that should be used as click trigger to select files.
                });

                this.dropzoneButtonsDisabled = ko.observable(true);

                dropzone.on("addedfile", function(file) {
                    self.dropzoneButtonsDisabled(false);
                });

                // Update the total progress bar
                dropzone.on("totaluploadprogress", function(progress) {
                    $("#dz-total-progress .progress-bar").css({
                        'width': progress + "%"
                    });
                });

                dropzone.on("sending", function(file) {
                    // Show the total progress bar when upload starts
                    document.querySelector("#dz-total-progress").style.opacity = "1";
                });

                // Hide the total progress bar when nothing's uploading anymore
                dropzone.on("queuecomplete", function(progress) {
                    document.querySelector("#dz-total-progress").style.opacity = "0";
                });

                this.uploadFiles = function() {
                    console.log('upload files');
                    //dropzone.enqueueFiles(dropzone.getFilesWithStatus(Dropzone.ADDED));
                }

                this.removeAllFiles = function() {
                    dropzone.removeAllFiles(true);
                    self.dropzoneButtonsDisabled(true);
                }

            }
        },
        template: {
            require: 'text!widget-templates/file'
        }
    });
});
