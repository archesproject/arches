define([
    'jquery',
    'knockout',
    'underscore',
    'arches',
    'dropzone',
    'uuid',
    'viewmodels/widget',
    'bindings/dropzone'
], function($, ko, _, arches, Dropzone, uuid, WidgetViewModel) {
    /**
     * A viewmodel used for viewing and uploading external resource data 
     *
     * @constructor
     * @name ExternalResourceDataViewModel
     *
     * @param  {string} params - a configuration object
     */

    

    VISIBLE_COLUMN_IDS = [
        "fca0475a-04fc-11eb-9978-02e99e44e93e",  /* species */
        "d7628ae4-3f2f-11eb-a2e2-73ab08a728ea",  /* date of observation */

    ]

    OBSERVATIONS_CSV_COLUMN_NAME_TO_NODE_IDS = {
        'ObserverName*': "0da1fe5e-04fd-11eb-9978-02e99e44e93e", 
        'ObserverContact*': "12bd77bb-04fd-11eb-9978-02e99e44e93e", 
        'ObserverAffiliation': "21f08600-04fd-11eb-9978-02e99e44e93e", 
        'SpeciesName*': "fca0475a-04fc-11eb-9978-02e99e44e93e", 
        'Positive Observation': "abdaf060-37ef-11eb-a206-acde48001122", 
        'SpDetermine': "", 
        'ID_Confidence': "", 
        'ObservationDate*': "d7628ae4-3f2f-11eb-a2e2-73ab08a728ea", 
        'NoPlantsObsvd*': "347a1450-3be2-11eb-8a94-acde48001122", 
        'Phenology': "347a1388-3be2-11eb-8a94-acde48001122", 
        'Collection': "", 
        'NoAnimalsObs': "fd0dd8bc-3be1-11eb-8a94-acde48001122", 
        'AnimalAgeClass': "fd0dd812-3be1-11eb-8a94-acde48001122", 
        'AnimalSiteUse*': "fd0dd6b4-3be1-11eb-8a94-acde48001122", 
        'AnimalBehavior*': "fd0dd5c4-3be1-11eb-8a94-acde48001122", 
        'AnimalDetectionMethod*': "fd0dd768-3be1-11eb-8a94-acde48001122", 
        'LocationDescription': "e9f6767e-033f-11eb-9978-02e99e44e93e", 
        'X_Coordinate*': {
            flag: 'format_location', 
            args: ['x'], 
            node_id: 'df79c02a-033f-11eb-9978-02e99e44e93e'
        }, 
        'Y_Coordinate*': {
            flag: 'format_location', 
            args: ['y'], 
            node_id: 'df79c02a-033f-11eb-9978-02e99e44e93e'
        }, 
        'CoordSource*': "fc55d878-033f-11eb-9978-02e99e44e93e", 
        'CoordAccuracy': "084ba470-050a-11eb-9978-02e99e44e93e", 
        'SurveyEffort*': "cd7dac4e-3be1-11eb-8a94-acde48001122", 
        'HabitatDesc': "a9cb687e-0340-11eb-9978-02e99e44e93e", 
        'SiteQuality': "b08729f0-0340-11eb-9978-02e99e44e93e", 
        'LandUse': "b94ac2ae-0340-11eb-9978-02e99e44e93e", 
        'Disturbances': "bffb3b10-0340-11eb-9978-02e99e44e93e", 
        'Threats': "c8b1ce90-0340-11eb-9978-02e99e44e93e", 
        'Comments': "bffb3b10-0340-11eb-9978-02e99e44e93e"
    }



    var ExternalResourceDataViewModel = function(params) {
        var self = this;

        params.configKeys = ['acceptedFiles', 'maxFilesize', 'maxFiles'];
        WidgetViewModel.apply(this, [params]);

        this.unique_id = uuid.generate();
        this.uniqueidClass = ko.computed(function() {
            return "unique_id_" + self.unique_id;
        });

        this.filter = ko.observable("");
        this.uploadMultiple = ko.observable(true);

        this.addedFiles = ko.observableArray();
        this.selectedFile = ko.observable(self.addedFiles()[0]);

        this.resourceModelNodeData = ko.observable();

        this.parsedFileData = ko.observableArray();
        this.parsedFileData.subscribe(function() {
            var hasMapData = self.parsedFileData().find(function(fileData) {
                return Object.values(fileData).find(function(value) {
                    return Boolean(value instanceof Object && value['geometry']['coordinates']);
                });
            });

            self.value({
                hasMapData: Boolean(hasMapData),
                data: self.parsedFileData(),
            })
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
            this.fetchResourceModelNodeData();
        };

        this.fetchResourceModelNodeData = function() {
            $.ajax({
                dataType: "json",
                url: arches.urls.graph_nodes(arches.resources[1]['graphid']),
                success: function (response) {
                    Object.values(response).forEach(function(nodeData) {
                        nodeData['visible'] = VISIBLE_COLUMN_IDS.some(function(columnId) { 
                            return columnId === nodeData.nodeid; 
                        });
                    });
                    self.resourceModelNodeData(response);
                }
            });
        };

        this.parseCSVFile = function(file) {
            var formData = new FormData();

            formData.append('uploaded_file', file);
            formData.append(
                'column_name_to_node_id_map', 
                JSON.stringify(OBSERVATIONS_CSV_COLUMN_NAME_TO_NODE_IDS)
            );

            $.ajax({
                dataType: "json",
                url: arches.urls.resource + '/data/',
                processData: false, /* important! */
                contentType: false, /* important! */
                method: 'POST',
                data: formData,
                success: function (response) {
                    self.addedFiles.push(file);

                    response.data.forEach(function(parsedRow) {
                        parsedRow['meta'] = {
                            'file': file,
                            'errors': ko.observable(parsedRow['errors']),
                        };

                        delete parsedRow['errors'];

                        self.parsedFileData.push(parsedRow);
                    });

                    console.log(response, self, params)
                }
            });
        };

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
                    self.parseCSVFile(file)
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
            self.selectedFile(file); 
        };

        this.removeFile = function(file) {
            self.addedFiles.remove(file)
        };

        this.reset = function() {
            if (self.dropzone) {
                self.dropzone.removeAllFiles(true);
                self.addedFiles.removeAll();
            }
        };

        this.initialize();
    };

    return ExternalResourceDataViewModel;
});