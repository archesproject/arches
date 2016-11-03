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
            params.configKeys = ['acceptedFiles', 'maxFilesize'];

            WidgetViewModel.apply(this, [params]);

            if (this.form) {
                this.form.on('after-update', function (res, tile) {
                    // TODO: detect if this widget was part of save, update value accordingly
                    // to reflect the uploaded state of files... maybe this:
                    console.log(self.tile === tile || _.contains(tile.tiles, self.tile))
                });
            }

            this.dropzoneButtonsDisabled = ko.observable(true);
            this.showProgressBar = ko.observable(false);
            this.progress = ko.observable(0);
            this.acceptedFiles.subscribe(function (val) {
                if (self.dropzone) {
                    self.dropzone.hiddenFileInput.setAttribute("accept", val);
                }
            });
            this.maxFilesize.subscribe(function (val) {
                if (self.dropzone) {
                    self.dropzone.options.maxFilesize = val;
                }
            });
            this.filesForUpload = ko.observableArray();

            this.filesForUpload.subscribe(function () {
                if (_.contains(self.formData.keys(), 'file-list_' + self.node.nodeid)) {
                    self.formData.delete('file-list_' + self.node.nodeid);
                }
                _.each(self.filesForUpload(), function (file) {
                    self.formData.append('file-list_' + self.node.nodeid, file, file.name);
                });
            });

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
                acceptedFiles: this.acceptedFiles(),
                maxFilesize: this.maxFilesize(),
                init: function () {
                    self.dropzone = this;

                    this.on("addedfile", function(file) {
                        self.dropzoneButtonsDisabled(false);
                        self.filesForUpload.push(file);
                    });

                    this.on("removedfile", function(file) {
                        self.filesForUpload.remove(file);
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
