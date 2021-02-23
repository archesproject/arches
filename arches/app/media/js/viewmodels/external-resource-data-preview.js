define([
    'jquery',
    'knockout',
    'underscore',
    'arches',
    'dropzone',
    'uuid',
    'viewmodels/file-widget',
    'bindings/dropzone',
], function($, ko, _, arches, Dropzone, uuid, FileWidgetViewModel) {
    $.getJSON(`${arches.urls.media}js/views/components/external-resource-data-preview/CSV_COLUMN_INFORMATION.json`, function(columnInformation) {
        GRAPH_ID = columnInformation['GRAPH_ID'];
        CSV_COLUMN_NAMES_TO_NODE_IDS = columnInformation['CSV_COLUMN_NAMES_TO_NODE_IDS'];
    })

    /**
     * A viewmodel used for viewing and uploading external resource data 
     *
     * @constructor
     * @name ExternalResourceDataPreviewViewModel
     *
     * @param  {string} params - a configuration object
     */

    var ExternalResourceDataPreviewViewModel = function(params) {
        var self = this;

        params.configKeys = ['acceptedFiles', 'maxFilesize', 'maxFiles'];
        FileWidgetViewModel.apply(this, [params]);

        this.acceptedFiles = ko.observable('.csv');
        this.maxFilesize = ko.observable(4);

        this.unique_id = uuid.generate();
        this.uniqueidClass = ko.computed(function() {
            return "unique_id_" + self.unique_id;
        });

        this.filter = ko.observable("");
        this.uploadMultiple = ko.observable(true);

        this.resourceModelNodeData = ko.observable();

        this.widget = params.widgets.find(function(widget) {
            return widget.datatype.datatype = 'resource-instance-list';
        })

        this.uncreatedResourceData = ko.pureComputed(function() {
            return self.fileData().reduce(function(acc, fileDatum) {
                fileDatum.data.forEach(function(resourceData) {
                    if (!fileDatum.created_resources[resourceData.row_id]) {
                        resourceData['file'] = fileDatum.file;
                        acc.push(resourceData);
                    }
                })
                return acc;
            }, []);
        });

        this.addedFiles = ko.pureComputed(function() {
            var files = {};

            self.uncreatedResourceData().forEach(function(resourceDatum) {
                if (!files[resourceDatum.file_id]) {
                    files[resourceDatum.file_id] = resourceDatum.file;
                }
            });

            return Object.values(files);
        });

        this.fileData = ko.observableArray();
        this.fileData.subscribe(function() {
            /* 
                hanging on tile because it persists through component refresh 
                safe because it's not persisted to the DB
            */ 
            self.tile._cachedFileData = self.fileData();

            params.fileData(self.fileData());
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
            uploadMultiple: self.uploadMultiple(),
            maxFiles: Number(this.maxFiles()),
            init: function() {
                self.dropzone = this;
                self.dropZoneInit();
            },
        };

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

        this.filteredList = ko.computed(function() {
            var arr = [], lowerName = "", filter = self.filter().toLowerCase();
            if(filter) {
                self.addedFiles().forEach(function(f, i) {
                    lowerName = f.name.toLowerCase();
                    if(lowerName.includes(filter)) { arr.push(self.addedFiles()[i]); }
                });
            }
            return arr;
        });

        this.initialize = function() {
            params.loading(true);

            if (ko.unwrap(params.tile._cachedFileData)) {
                self.fileData(ko.unwrap(params.tile._cachedFileData))
            }

            this.fetchResourceModelNodeData();

            params.loading(false);
        };

        this.fetchResourceModelNodeData = function() {
            params.loading(true);

            $.ajax({
                dataType: "json",
                url: arches.urls.graph_nodes(GRAPH_ID),
                success: function (response) {
                    self.resourceModelNodeData(response);
                    params.loading(false);
                }
            });
        };

        this.parseCSVFile = function(file) {
            params.loading(true);

            var formData = new FormData();

            formData.append('uploaded_file', file);
            formData.append(
                'column_name_to_node_data_map', 
                JSON.stringify(CSV_COLUMN_NAMES_TO_NODE_IDS)
            );

            $.ajax({
                dataType: "json",
                url: arches.urls.api_external_resource_data_validation,
                processData: false, /* important! */
                contentType: false, /* important! */
                method: 'POST',
                data: formData,
                success: function (response) {
                    response.data.forEach(function(parsedRow) {
                        parsedRow['errors'] = ko.observable(parsedRow['errors']);
                        parsedRow['file_id'] = file.upload.uuid;
                    });

                    response['file'] = file;
                    response['created_resources'] = {};

                    self.fileData.push(response);
                    params.loading(false);
                }
            });
        };

        this.createResources = function() {
            params.loading(true);

            $.ajax({
                dataType: "json",
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({
                    'file_data': self.fileData(),
                    'column_name_to_node_data_map': CSV_COLUMN_NAMES_TO_NODE_IDS,
                }),
                url: arches.urls.api_external_resource_creation(graphid=GRAPH_ID),
                success: function(response) {
                    self.fileData(response['file_data']);

                    var resourceInstanceIds = response['file_data'].reduce(function(acc, fileDatum) {
                        Object.values(fileDatum.created_resources).forEach(function(resourceData) {
                            acc.push(resourceData['resourceinstance_id']);
                        });
                        return acc;
                    }, []);

                    var widgetData = resourceInstanceIds.map(function(resourceInstanceId) {
                        return {
                            resourceId: resourceInstanceId,
                            ontologyProperty: '',
                            inverseOntologyProperty: '',
                        };
                    });

                    params.tile.data[self.widget.node_id()](widgetData);

                    params.tile.save().then(function() {
                        params.loading(false);
                    })
                },
            });
        }

        this.validateNodeData = function(parsedFile, nodeId, cellValue) {
            /* 
                we should refactor this to use a cancellable event that fires only 
                after the user has stopped interacting with the input for some amount of time 
            */ 
            $.ajax({
                dataType: "json",
                url: arches.urls.resource + '/node_data/',
                method: 'POST',
                data: {
                    node_id: JSON.stringify(nodeId),
                    cell_value: JSON.stringify(cellValue)
                },
                success: function (response) {
                    var errors = parsedFile.meta.errors();
                    
                    if (response.errors.length) {
                        errors[nodeId] = response.errors;
                    }
                    else {
                        delete errors[nodeId];
                    }

                    parsedFile.meta.errors(errors);
                }
            });
        };

        this.dropZoneInit = function() {
            self.dropzone.on("addedfile", function(file) {
                if (file.type === 'text/csv') {
                    self.parseCSVFile(file);
                }
            });

            self.dropzone.on("error", function(file, error) {
                file.error = error;
                /* ALERT USER HERE */ 
            });

            self.dropzone.on("removedfile", function(file) {
            });
        }

        this.formatSize = function(file) {
            var bytes = ko.unwrap(file.size);
            if(bytes == 0) return '0 Byte';
            var k = 1024;
            var dm = 2;
            var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
            var i = Math.floor(Math.log(bytes) / Math.log(k));
            return '<span>' + parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + '</span> ' + sizes[i];
        };

        this.selectFile = function(file) { 
            // self.selectedFile(file); 
        };

        this.deleteResourceDatum = function(rowId) {
            var fileData = self.fileData();

            var filteredFileData = fileData.filter(function(fileDatum) {
                fileDatum.data = fileDatum.data.filter(function(rowData) {
                    return rowData.row_id !== rowId;
                });

                return fileDatum.data.length;
            });
            
            self.fileData(filteredFileData);
        };

        this.removeFile = function(file) {
            // self.addedFiles.remove(file)
        };

        this.reset = function() {
            if (self.dropzone) {
                self.dropzone.removeAllFiles(true);
                // self.addedFiles.removeAll();
            }
        };

        this.initialize();
    };

    ko.components.register('external-resource-data-preview', {
        viewModel: ExternalResourceDataPreviewViewModel,
        template: {
            require: 'text!templates/views/components/external-resource-data-preview.htm'
        }
    });

    return ExternalResourceDataPreviewViewModel;
});