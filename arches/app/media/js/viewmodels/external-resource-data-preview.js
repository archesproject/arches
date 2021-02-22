define([
    'jquery',
    'knockout',
    'underscore',
    'arches',
    'dropzone',
    'uuid',
    'viewmodels/file-widget',
    'bindings/dropzone'
], function($, ko, _, arches, Dropzone, uuid, FileWidgetViewModel) {
    /**
     * A viewmodel used for viewing and uploading external resource data 
     *
     * @constructor
     * @name ExternalResourceDataPreviewViewModel
     *
     * @param  {string} params - a configuration object
     */


    OBSERVATIONS_GRAPH_ID = "d41455df-033e-11eb-9978-02e99e44e93e";

    OBSERVATIONS_CSV_COLUMN_NAME_TO_NODE_IDS = {
        'ObservationDate*': { 
            node_id: "d7628ae4-3f2f-11eb-a2e2-73ab08a728ea",
            nodegroup_id: "f56cd124-04fc-11eb-9978-02e99e44e93e",
            visible: true,
        }, 
        'SpeciesName*': { 
            node_id: "fca0475a-04fc-11eb-9978-02e99e44e93e",
            nodegroup_id: "f56cd124-04fc-11eb-9978-02e99e44e93e",
            visible: true,
         }, 
         'ObserverName*': { 
            node_id: "0da1fe5e-04fd-11eb-9978-02e99e44e93e",
            nodegroup_id: "f56cd124-04fc-11eb-9978-02e99e44e93e",
         }, 
        'ObserverContact*': { 
            node_id: "12bd77bb-04fd-11eb-9978-02e99e44e93e",
            nodegroup_id: "f56cd124-04fc-11eb-9978-02e99e44e93e",
        }, 
        'ObserverAffiliation': { 
            node_id: "21f08600-04fd-11eb-9978-02e99e44e93e",
            nodegroup_id: "f56cd124-04fc-11eb-9978-02e99e44e93e",
        }, 
        'Detection Status': { 
            node_id: "abdaf060-37ef-11eb-a206-acde48001122",
            nodegroup_id: "f56cd124-04fc-11eb-9978-02e99e44e93e",
         }, 
        'SpDetermine': { 
            node_id: ""
         }, 
        'ID_Confidence': { 
            node_id: ""
         }, 
        'NoPlantsObsvd*': { 
            node_id: "347a1450-3be2-11eb-8a94-acde48001122",
            nodegroup_id: "347a10fe-3be2-11eb-8a94-acde48001122",
         }, 
        'Phenology': { 
            node_id: "347a1388-3be2-11eb-8a94-acde48001122",
            nodegroup_id: "347a10fe-3be2-11eb-8a94-acde48001122",
         }, 
        'Collection': { 
            node_id: ""
         }, 
        'NoAnimalsObs': { 
            node_id: "fd0dd8bc-3be1-11eb-8a94-acde48001122",
            nodegroup_id: "fd0dd2a4-3be1-11eb-8a94-acde48001122",
         }, 
        'AnimalAgeClass': { 
            node_id: "fd0dd812-3be1-11eb-8a94-acde48001122",
            nodegroup_id: "fd0dd2a4-3be1-11eb-8a94-acde48001122",
         }, 
        'AnimalSiteUse*': { 
            node_id: "fd0dd6b4-3be1-11eb-8a94-acde48001122",
            nodegroup_id: "fd0dd2a4-3be1-11eb-8a94-acde48001122",
         }, 
        'AnimalBehavior*': { 
            node_id: "fd0dd5c4-3be1-11eb-8a94-acde48001122",
            nodegroup_id: "fd0dd2a4-3be1-11eb-8a94-acde48001122",
        }, 
        'AnimalDetectionMethod*': { 
            node_id: "fd0dd768-3be1-11eb-8a94-acde48001122",
            nodegroup_id: "fd0dd2a4-3be1-11eb-8a94-acde48001122",
         }, 
        'LocationDescription': { 
            node_id: "e9f6767e-033f-11eb-9978-02e99e44e93e",
            nodegroup_id: "b959d86c-033f-11eb-9978-02e99e44e93e",
         }, 
        'X_Coordinate*': {
            flag: 'format_location', 
            args: ['x'], 
            node_id: 'df79c02a-033f-11eb-9978-02e99e44e93e',
            nodegroup_id: "b959d86c-033f-11eb-9978-02e99e44e93e",
        }, 
        'Y_Coordinate*': {
            flag: 'format_location', 
            args: ['y'], 
            node_id: 'df79c02a-033f-11eb-9978-02e99e44e93e',
            nodegroup_id: "b959d86c-033f-11eb-9978-02e99e44e93e",
        }, 
        'CoordSource*': { 
            node_id: "fc55d878-033f-11eb-9978-02e99e44e93e",
            nodegroup_id: "b959d86c-033f-11eb-9978-02e99e44e93e",
         }, 
        'CoordAccuracy': { 
            node_id: "084ba470-050a-11eb-9978-02e99e44e93e",
            nodegroup_id: "b959d86c-033f-11eb-9978-02e99e44e93e",
         }, 
        'SurveyEffort*': { 
            node_id: "cd7dac4e-3be1-11eb-8a94-acde48001122",
            nodegroup_id: "f56cd124-04fc-11eb-9978-02e99e44e93e",
         }, 
        'HabitatDesc': { 
            node_id: "a9cb687e-0340-11eb-9978-02e99e44e93e",
            nodegroup_id: "9b047be6-0340-11eb-9978-02e99e44e93e",
         }, 
        'SiteQuality': { 
            node_id: "b08729f0-0340-11eb-9978-02e99e44e93e",
            nodegroup_id: "9b047be6-0340-11eb-9978-02e99e44e93e",
         }, 
        'LandUse': { 
            node_id: "b94ac2ae-0340-11eb-9978-02e99e44e93e",
            nodegroup_id: "9b047be6-0340-11eb-9978-02e99e44e93e",
         }, 
        'Disturbances': { 
            node_id: "bffb3b10-0340-11eb-9978-02e99e44e93e",
            nodegroup_id: "9b047be6-0340-11eb-9978-02e99e44e93e",
        }, 
        'Threats': { 
            node_id: "c8b1ce90-0340-11eb-9978-02e99e44e93e",
            nodegroup_id: "9b047be6-0340-11eb-9978-02e99e44e93e",
         }, 
        'Comments': { 
            node_id: "40417046-0341-11eb-9978-02e99e44e93e",
            nodegroup_id: "40417046-0341-11eb-9978-02e99e44e93e",
        }
    }



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
                url: arches.urls.graph_nodes(OBSERVATIONS_GRAPH_ID),
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
                JSON.stringify(OBSERVATIONS_CSV_COLUMN_NAME_TO_NODE_IDS)
            );

            $.ajax({
                dataType: "json",
                url: arches.urls.api_external_resource_data,
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
                    'column_name_to_node_data_map': OBSERVATIONS_CSV_COLUMN_NAME_TO_NODE_IDS,
                }),
                url: arches.urls.api_external_foobar(graphid=OBSERVATIONS_GRAPH_ID),
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