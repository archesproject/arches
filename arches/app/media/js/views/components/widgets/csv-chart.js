define([
    'jquery',
    'knockout',
    'knockout-mapping',
    'underscore',
    'dropzone',
    'nvd3',
    'uuid',
    'moment',
    'viewmodels/widget',
    'arches',
    'bindings/dropzone',
    'bindings/nvd3-line',
    // 'bindings/datatable',
    'bindings/chosen',
], function($, ko, koMapping, _, Dropzone, nvd3, uuid, moment, WidgetViewModel, arches) {
    /**
     * registers a file-widget component for use in forms
     * @function external:"ko.components".file-widget
     * @param {object} params
     * @param {string} params.value - the value being managed
     * @param {function} params.config - observable containing config object
     * @param {string} params.config().acceptedFiles - accept attribute value for file input
     * @param {string} params.config().maxFilesize - maximum allowed file size in MB
     */
    return ko.components.register('csv-chart-widget', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['acceptedFiles', 'maxFilesize'];

            WidgetViewModel.apply(this, [params]);
            this.selectedFile = ko.observable();
            this.viewChart = ko.observable(false);

            this.selectionDisplayValues = ko.computed(function() {
                if (this.selectedFile()) {
                    var f = this.selectedFile()
                    res = {
                        file_name: ko.unwrap(f.name),
                        upload_time: moment(ko.unwrap(f.upload_time)).format('YYYY-MM-DD'),
                        size: ko.unwrap(f.size)/1024 + 'kb',
                        url: ko.unwrap(f.url),
                        records: this.chartData().length === 0 ? undefined : this.chartData()[0].values.length
                    };
                    return res;
                } else {
                    return {
                        upload_time: undefined,
                        size: undefined,
                        records: undefined,
                        file_name: undefined
                    }
                }

            }, this);

            if (this.form) {
                this.form.on('after-update', function(req, tile) {
                    if (tile.isParent === true){
                        if (self.dropzone) {
                            self.dropzone.removeAllFiles(true);
                        }
                    } else if ((self.tile === tile || _.contains(tile.tiles, self.tile)) && req.status === 200) {
                        if (self.filesForUpload().length > 0) {
                            self.filesForUpload.removeAll();
                        }
                        var data = req.responseJSON.data[self.node.nodeid] || req.responseJSON.tiles[self.node.nodeid][0].data[self.node.nodeid];
                        if (Array.isArray(data.files)) {
                            self.uploadedFiles(data.files)
                        }
                        self.dropzone.removeAllFiles(true);
                        self.formData.delete('file-list_' + self.node.nodeid);
                    }
                });
                this.form.on('tile-reset', function(tile) {
                    if ((self.tile === tile || _.contains(tile.tiles, self.tile))) {
                        var value = ko.unwrap(self.value);
                        if (self.filesForUpload().length > 0) {
                            self.filesForUpload.removeAll();
                        }
                        if (Array.isArray(value.files)) {
                            self.uploadedFiles(value.files)
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
            if (ko.isObservable(self.value)) {
                if (self.value()) {
                    if (Array.isArray(self.value().files)) {
                        this.uploadedFiles(self.value().files);
                    }
                }
            } else {
                if (Array.isArray(self.value.files())) {
                    this.uploadedFiles(self.value.files());
                }
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

            this.selectedUrl = ko.observable('')
            this.selectedFiles = ko.observableArray([]);

            this.indicateDataTableRowSelection = function(row) {
                this.selectedFiles.removeAll();
                this.selectedFiles.push(ko.unwrap(row.url))
            }

            if (!ko.isObservable(this.value)) {
                this.datasetName = this.value.name;
                this.datasetDescription = this.value.description;
                this.datasetDevice = this.value.device;
            } else {
                this.datasetName = ko.observable('');
                this.datasetDescription = ko.observable('');
                this.datasetDevice = ko.observable('');
            };

            [this.datasetName, this.datasetDescription, this.datasetDevice].forEach(function(obs){
                var self = this;
                obs.subscribe(function(val){
                    if (ko.isObservable(self.value)){
                        this.value({'files':this.filesJSON(), 'name':this.datasetName(), 'description':this.datasetDescription(), 'device':this.datasetDevice()})
                    }
                }, self)
            }, this);

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
                            error: file.error,
                            upload_time: Date.now()
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

                if (ko.unwrap(self.value) !== null || self.filesForUpload().length !== 0 || self.uploadedFiles().length !== 0) {
                    if (ko.isObservable(self.value)){
                        self.value(
                            {'files':value.filter(function(file) {
                                return file.accepted;
                            }),
                             'name':self.datasetName(),
                             'description':self.datasetDescription(),
                             'device':self.datasetDevice()
                            })
                    } else {
                        self.value.files(value.filter(function(file) {
                            return file.accepted;
                        }));
                    }
                }

            });

            this.chartData = ko.observable([])
            this.resize = function(){
                var self = this;
                var reloadChart = function() {
                    self.getFileData(self.uploadedFiles()[0])
                    window.dispatchEvent(new Event('resize'))
                    }
                    window.setTimeout(reloadChart, 50)
                }



            this.getFileData = function(f) {
                var self = this;
                var url = ko.unwrap(f.url);
                var filename = ko.unwrap(f.name);
                var basename = filename.substr(0, filename.lastIndexOf('.')) || filename;
                if (url.endsWith('.csv')) {
                    d3.csv(url, function(d) {
                      return {
                        x: +d.x,
                        y: +d.y,
                      };
                    }, function(error, rows) {
                        var data = _.sortBy(rows, function(a){return a['x']});
                      self.chartData(data)
                  });
              } else {
                  d3.text(url, function(text) {
                    var rows = d3.tsv.parseRows(text).map(function(row) {
                      return {
                          x: +row[0],
                          y: +row[1]
                          }
                    })
                    var data = _.sortBy(rows, function(a){return a['x']});
                    var series = [{values: data, key: basename, color: '#ff7f0e'}]

                    self.chartData(series);
                    self.selectedFile(f);
                  });
              }
            }

            this.selectedUrl.subscribe(function(val){
                var url = val;
                if (this.uploadedFiles().length > 0 && url) {
                    var selected = _.filter(this.uploadedFiles(), function(f){return ko.unwrap(f.url) === url})[0]
                    this.selectedFile(url);
                    this.getFileData(selected);
                }

                // this.indicateDataTableRowSelection(selected) //Only needed if we keep table
            }, this)

            this.unique_id = uuid.generate();
            this.uniqueidClass = ko.computed(function () {
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
            require: 'text!widget-templates/csv-chart'
        }
    });
});
