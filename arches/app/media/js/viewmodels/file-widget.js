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
     * A viewmodel used for domain widgets
     *
     * @constructor
     * @name FileWidgetViewModel
     *
     * @param  {string} params - a configuration object
     */
    var FileWidgetViewModel = function(params) {
        var self = this;
        params.configKeys = ['acceptedFiles', 'maxFilesize', 'maxFiles'];

        WidgetViewModel.apply(this, [params]);

        this.uploadMulti = ko.observable(true);
        this.filesForUpload = ko.observableArray();
        this.uploadedFiles = ko.observableArray();
        this.unsupportedImageTypes = ['tif', 'tiff', 'vnd.adobe.photoshop'];


        if (this.form) {
            this.form.on('after-update', function(req, tile) {
                var hasdata = _.filter(tile.data, function(val, key) {
                    val = ko.unwrap(val);
                    if (val) {
                        return val;
                    }
                });
                if (tile.isParent === true || hasdata.length === 0){
                    if (self.dropzone) {
                        self.dropzone.removeAllFiles(true);
                    }
                } else if ((self.tile === tile || _.contains(tile.tiles, self.tile)) && req.status === 200) {
                    if (self.filesForUpload().length > 0) {
                        self.filesForUpload.removeAll();
                    }
                    var data = req.responseJSON.data[self.node.nodeid];
                    if (Array.isArray(data)) {
                        self.uploadedFiles(data);
                    }
                    if (self.dropzone) {
                        self.dropzone.removeAllFiles(true);
                    }
                    self.formData.delete('file-list_' + self.node.nodeid);
                }
            });
            this.form.on('tile-reset', function(tile) {
                if ((self.tile === tile || _.contains(tile.tiles, self.tile))) {
                    if (self.filesForUpload().length > 0) {
                        self.filesForUpload.removeAll();
                    }
                    if (Array.isArray(self.value())) {
                        var uploaded = _.filter(self.value(), function(val) {
                            return ko.unwrap(val.status) === 'uploaded';
                        });
                        self.uploadedFiles(uploaded);
                    }
                    if (self.dropzone) {
                        self.dropzone.removeAllFiles(true);
                        self.formData.delete('file-list_' + self.node.nodeid);
                    }
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

        this.formatSize = function(file) {
            var bytes = ko.unwrap(file.size);
            if(bytes == 0) return '0 Byte';
            var k = 1024;
            var dm = 2;
            var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
            var i = Math.floor(Math.log(bytes) / Math.log(k));
            return '<span>' + parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + '</span> ' + sizes[i];
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
            if (self.formData) {
                if (_.contains(self.formData.keys(), 'file-list_' + self.node.nodeid)) {
                    self.formData.delete('file-list_' + self.node.nodeid);
                }
            }
            if (value.length > 1 && self.selectedFile() == undefined) { self.selectedFile(value[0]); }
            _.each(self.filesForUpload(), function(file) {
                if (file.accepted) {
                    self.formData.append('file-list_' + self.node.nodeid, file, file.name);
                }
            });
            if (ko.unwrap(self.value) !== null || self.filesForUpload().length !== 0 || self.uploadedFiles().length !== 0) {
                self.value(
                    value.filter(function(file) {
                        return file.accepted;
                    })
                );
            }
        });

        if (Array.isArray(self.value())) {
            this.uploadedFiles(self.value());
        }
        this.filter = ko.observable("");
        this.filteredList = ko.computed(function() {
            var arr = [], lowerName = "", filter = self.filter().toLowerCase();
            if(filter) {
                self.filesJSON().forEach(function(f, i) {
                    lowerName = f.name.toLowerCase();
                    if(lowerName.includes(filter)) { arr.push(self.filesJSON()[i]); }
                });
            }
            return arr;
        });

        this.selectedFile = ko.observable(self.filesJSON()[0]);
        this.selectFile = function(sFile) { self.selectedFile(sFile); };

        this.removeFile = function(file) {
            var filePosition;
            self.filesJSON().forEach(function(f, i) { if (f.file_id === file.file_id) { filePosition = i; } });
            var newfilePosition = filePosition === 0 ? 1 : filePosition - 1;
            var filesForUpload = self.filesForUpload();
            var uploadedFiles = self.uploadedFiles();
            if (file.file_id) {
                file = _.find(uploadedFiles, function(uploadedFile) {
                    return file.file_id ===  ko.unwrap(uploadedFile.file_id);
                });
                self.uploadedFiles.remove(file);
            } else {
                file = filesForUpload[file.index];
                self.filesForUpload.remove(file);
            }
            if (self.filesJSON().length > 0) { self.selectedFile(self.filesJSON()[newfilePosition]); }
        };
        
        this.pageCt = ko.observable(5);
        this.pageCtReached = ko.computed(function() {
            return (self.filesJSON().length > self.pageCt() ? 'visible' : 'hidden');
        });

        this.pagedList = function(list) {
            var arr = [], i = 0;
            if(list.length > self.pageCt()) {
                while(arr.length < self.pageCt()) { arr.push(list[i++]); }
                return arr;
            }
            return list;
        };

        this.unique_id = uuid.generate();
        this.uniqueidClass = ko.computed(function() {
            return "unique_id_" + self.unique_id;
        });

        this.dropzoneOptions = {
            url: "arches.urls.root",
            dictDefaultMessage: '',
            autoProcessQueue: false,
            previewTemplate: $("template#file-widget-dz-preview").html(),
            autoQueue: false,
            previewsContainer: ".dz-previews." + this.uniqueidClass(),
            clickable: ".fileinput-button." + this.uniqueidClass(),
            acceptedFiles: this.acceptedFiles(),
            maxFilesize: this.maxFilesize(),
            uploadMultiple: self.uploadMulti(),
            // maxFiles: Number(this.maxFiles()),
            init: function() {
                self.dropzone = this;

                this.on("addedfile", function(file) {
                    self.filesForUpload.push(file);
                });

                this.on("error", function(file, error) {
                    file.error = error;
                    self.filesForUpload.valueHasMutated();
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
            return self.uploadedFiles().length === 1 ? ko.unwrap(self.uploadedFiles()[0].name) : self.uploadedFiles().length; 
        });

        this.reportFiles = ko.computed(function() {
            return self.uploadedFiles().filter(function(file) {
                var fileType = ko.unwrap(file.type);
                if (fileType) {
                    var ext = fileType.split('/').pop();
                    return fileType.indexOf('image') < 0 || self.unsupportedImageTypes.indexOf(ext) > -1;
                }
                return true;
            });
        });

        this.reportImages = ko.computed(function() {
            return self.uploadedFiles().filter(function(file) {
                var fileType = ko.unwrap(file.type);
                if (fileType) {
                    var ext = fileType.split('/').pop();
                    return fileType.indexOf('image') >= 0 && self.unsupportedImageTypes.indexOf(ext) <= 0;
                }
                return false;
            });
        });
    };

    return FileWidgetViewModel;
});
