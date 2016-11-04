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
                this.form.on('after-update', function(req, tile) {
                    if ((self.tile === tile || _.contains(tile.tiles, self.tile)) && req.status === 200) {
                        if (self.filesForUpload().length > 0) {
                            self.filesForUpload.removeAll();
                        }
                        var data = req.responseJSON.data[self.node.nodeid];
                        if (Array.isArray(data)) {
                            self.uploadedFiles(data)
                        }
                        self.dropzone.removeAllFiles(true);
                        self.formData.delete('file-list_' + self.node.nodeid);
                    }
                });
            }

            this.acceptedFiles.subscribe(function(val) {
                if (self.dropzone) {
                    self.dropzone.hiddenFileInput.setAttribute("accept", val);
                }
            });
            this.maxFilesize.subscribe(function(val) {
                if (self.dropzone) {
                    self.dropzone.options.maxFilesize = val;
                }
            });

            this.filesForUpload = ko.observableArray();
            this.uploadedFiles = ko.observableArray();
            if (Array.isArray(self.value())) {
                this.uploadedFiles(self.value());
            }
            this.removeUploadedFile = function(file) {
                self.uploadedFiles.remove(file);
            }

            this.formatSize = function (file) {
                var bytes = ko.unwrap(file.size);
                if(bytes == 0) return '0 Byte';
                var k = 1000; // or 1024 for binary
                var dm = 2;
                var sizes = ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PB', 'EB', 'ZB', 'YB'];
                var i = Math.floor(Math.log(bytes) / Math.log(k));
                return '<strong>' + parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + '</strong> ' + sizes[i];
            };

            var filesJSON = ko.computed(function() {
                var filesForUpload = self.filesForUpload();
                var uploadedFiles = self.uploadedFiles();
                if (_.contains(self.formData.keys(), 'file-list_' + self.node.nodeid)) {
                    self.formData.delete('file-list_' + self.node.nodeid);
                }
                var filesForUpload = self.filesForUpload()
                    .filter(function(file) {
                        return file.accepted;
                    });
                _.each(filesForUpload, function(file) {
                    self.formData.append('file-list_' + self.node.nodeid, file, file.name);
                });
                return uploadedFiles.concat(
                    _.map(filesForUpload, function(file) {
                        return {
                            name: file.name,
                            accepted: file.accepted,
                            height: file.height,
                            lastModified: file.lastModified,
                            size: file.size,
                            status: file.status,
                            type: file.type,
                            width: file.width,
                            url: null,
                            file_id: null
                        };
                    })
                );
            }).extend({throttle: 100});

            filesJSON.subscribe(function(value) {
                self.value(value);
            });

            this.dropzoneOptions = {
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
                init: function() {
                    self.dropzone = this;

                    this.on("addedfile", function(file) {
                        self.filesForUpload.push(file);
                    });

                    this.on("removedfile", function(file) {
                        self.filesForUpload.remove(file);
                    });
                }
            };

            this.reset = function() {
                if (self.dropzone) {
                    self.dropzone.removeAllFiles(true);
                }
            };

            this.displayValue = ko.computed(function() {
                return self.uploadedFiles().length;
            });
        },
        template: {
            require: 'text!widget-templates/file'
        }
    });
});
