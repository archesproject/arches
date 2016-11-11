define([
    'jquery',
    'knockout',
    'underscore',
    'dropzone',
    'uuid',
    'viewmodels/widget',
    'bindings/dropzone'
], function($, ko, _, Dropzone, uuid, WidgetViewModel) {
    /**
     * registers a file-widget component for use in forms
     * @function external:"ko.components".file-widget
     * @param {object} params
     * @param {string} params.value - the value being managed
     * @param {function} params.config - observable containing config object
     * @param {string} params.config().acceptedFiles - accept attribute value for file input
     * @param {string} params.config().maxFilesize - maximum allowed file size in MB
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
                this.form.on('tile-reset', function(tile) {
                    if ((self.tile === tile || _.contains(tile.tiles, self.tile))) {
                        if (self.filesForUpload().length > 0) {
                            self.filesForUpload.removeAll();
                        }
                        if (Array.isArray(self.value())) {
                            self.uploadedFiles(self.value())
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
            this.removeFile = function(file) {
                var filesForUpload = self.filesForUpload();
                var uploadedFiles = self.uploadedFiles();
                if (file.file_id) {
                    file = _.find(uploadedFiles, function (uploadedFile) {
                        return file.file_id ===  ko.unwrap(uploadedFile.file_id);
                    });
                    self.uploadedFiles.remove(file);
                } else {
                    file = filesForUpload[file.index];
                    self.filesForUpload.remove(file);
                }
            }

            this.formatSize = function (file) {
                var bytes = ko.unwrap(file.size);
                if(bytes == 0) return '0 Byte';
                var k = 1024;
                var dm = 2;
                var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
                var i = Math.floor(Math.log(bytes) / Math.log(k));
                return '<strong>' + parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + '</strong> ' + sizes[i];
            };

            this.filesJSON = ko.computed(function() {
                var filesForUpload = self.filesForUpload();
                var uploadedFiles = self.uploadedFiles();
                return ko.toJS(uploadedFiles.concat(
                    _.map(filesForUpload, function(file, i) {
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
                            file_id: null,
                            index: i,
                            content: URL.createObjectURL(file),
                            error: file.error
                        };
                    })
                ));
            }).extend({throttle: 100});

            this.filesJSON.subscribe(function(value) {
                if (_.contains(self.formData.keys(), 'file-list_' + self.node.nodeid)) {
                    self.formData.delete('file-list_' + self.node.nodeid);
                }
                _.each(self.filesForUpload(), function(file) {
                    if (file.accepted) {
                        self.formData.append('file-list_' + self.node.nodeid, file, file.name);
                    }
                });
                self.value(
                    value.filter(function(file) {
                        return file.accepted;
                    })
                );
            });

            this.unique_id = uuid.generate();
            this.uniqueidClass = ko.computed(function () {
                return "unique_id_" + self.unique_id;
            });

            this.dropzoneOptions = {
                url: "/",
                dictDefaultMessage: '',
                autoProcessQueue: false,
                previewTemplate: $("template#file-widget-dz-preview").html(),
                autoQueue: false,
                previewsContainer: ".dz-previews." + this.uniqueidClass(),
                clickable: ".fileinput-button." + this.uniqueidClass(),
                acceptedFiles: this.acceptedFiles(),
                maxFilesize: this.maxFilesize(),
                init: function() {
                    self.dropzone = this;

                    this.on("addedfile", function(file) {
                        self.filesForUpload.push(file);
                    });

                    this.on("error", function(file, error) {
                        file.error = error;
                        self.filesForUpload.valueHasMutated()
                    });

                    this.on("removedfile", function(file) {
                        self.filesForUpload.remove(file);
                    });
                }
            };

            this.reset = function() {
                if (self.dropzone) {
                    self.dropzone.removeAllFiles(true);
                    self.uploadedFiles.removeAll();
                    self.filesForUpload.removeAll();
                }
            };

            this.displayValue = ko.computed(function() {
                return self.uploadedFiles().length;
            });

            this.reportFiles = ko.computed(function() {
                return self.uploadedFiles().filter(function(file) {
                    return ko.unwrap(file.type).indexOf('image') < 0;
                });
            });

            this.reportImages = ko.computed(function() {
                return self.uploadedFiles().filter(function(file) {
                    return ko.unwrap(file.type).indexOf('image') >= 0;
                });
            });

        },
        template: {
            require: 'text!widget-templates/file'
        }
    });
});
