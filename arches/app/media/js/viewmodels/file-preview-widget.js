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


    OBSERVATIONS_GRAPH_ID = "d41455df-033e-11eb-9978-02e99e44e93e";

    OBSERVATIONS_CSV_COLUMN_NAME_TO_NODE_IDS = {
        'ObserverName*': { 
            node_id: "0da1fe5e-04fd-11eb-9978-02e99e44e93e"
         }, 
        'ObserverContact*': { 
            node_id: "12bd77bb-04fd-11eb-9978-02e99e44e93e"
         }, 
        'ObserverAffiliation': { 
            node_id: "21f08600-04fd-11eb-9978-02e99e44e93e"
         }, 
        'SpeciesName*': { 
            node_id: "fca0475a-04fc-11eb-9978-02e99e44e93e",
            visibile: true,
         }, 
        'Positive Observation': { 
            node_id: "abdaf060-37ef-11eb-a206-acde48001122"
         }, 
        'SpDetermine': { 
            node_id: ""
         }, 
        'ID_Confidence': { 
            node_id: ""
         }, 
        'ObservationDate*': { 
            node_id: "d7628ae4-3f2f-11eb-a2e2-73ab08a728ea",
            visibile: true,
         }, 
        'NoPlantsObsvd*': { 
            node_id: "347a1450-3be2-11eb-8a94-acde48001122"
         }, 
        'Phenology': { 
            node_id: "347a1388-3be2-11eb-8a94-acde48001122"
         }, 
        'Collection': { 
            node_id: ""
         }, 
        'NoAnimalsObs': { 
            node_id: "fd0dd8bc-3be1-11eb-8a94-acde48001122"
         }, 
        'AnimalAgeClass': { 
            node_id: "fd0dd812-3be1-11eb-8a94-acde48001122"
         }, 
        'AnimalSiteUse*': { 
            node_id: "fd0dd6b4-3be1-11eb-8a94-acde48001122"
         }, 
        'AnimalBehavior*': { 
            node_id: "fd0dd5c4-3be1-11eb-8a94-acde48001122"
         }, 
        'AnimalDetectionMethod*': { 
            node_id: "fd0dd768-3be1-11eb-8a94-acde48001122"
         }, 
        'LocationDescription': { 
            node_id: "e9f6767e-033f-11eb-9978-02e99e44e93e"
         }, 
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
        'CoordSource*': { 
            node_id: "fc55d878-033f-11eb-9978-02e99e44e93e"
         }, 
        'CoordAccuracy': { 
            node_id: "084ba470-050a-11eb-9978-02e99e44e93e"
         }, 
        'SurveyEffort*': { 
            node_id: "cd7dac4e-3be1-11eb-8a94-acde48001122"
         }, 
        'HabitatDesc': { 
            node_id: "a9cb687e-0340-11eb-9978-02e99e44e93e"
         }, 
        'SiteQuality': { 
            node_id: "b08729f0-0340-11eb-9978-02e99e44e93e"
         }, 
        'LandUse': { 
            node_id: "b94ac2ae-0340-11eb-9978-02e99e44e93e"
         }, 
        'Disturbances': { 
            node_id: "bffb3b10-0340-11eb-9978-02e99e44e93e"
         }, 
        'Threats': { 
            node_id: "c8b1ce90-0340-11eb-9978-02e99e44e93e"
         }, 
        'Comments': { 
            node_id: "bffb3b10-0340-11eb-9978-02e99e44e93e"
        }
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
        this.addedFiles.subscribe(function(file) {
            self.selectedFile(file[0])
        });
        this.selectedFile = ko.observable();

        this.resourceModelNodeData = ko.observable();

        this.fileData = ko.observableArray();
        this.fileData.subscribe(function() {
            // var value = {
            //     nodeId: self.node.id,
            //     data: self.parsedFileData(),
            //     addedFiles: self.addedFiles(),
            // };

            self.value(self.fileData())
        });


        this.createdResources = ko.observableArray();





        if (self.value()) {
            // var uploadedFiles = {};
            self.fileData(self.value())

            console.log(self.value())

            // if (self.value().data) {
            //     self.value().data.forEach(function(foo) {
            //         self.parsedFileData.push(foo);
    
            //         var fileId = foo.file_id;
    
            //         if (!uploadedFiles[fileId]) {
            //             uploadedFiles[fileId] = foo.meta.file;
            //         }
    
            //         self.addedFiles(Object.values(uploadedFiles));
            //     });
            // }
            // else {
            //     Object.values(self.value()).forEach(function(foo) {
            //         self.parsedFileData.push(foo);
    
            //         var fileId = foo.meta.file.upload.uuid;
    
            //         if (!uploadedFiles[fileId]) {
            //             uploadedFiles[fileId] = foo.meta.file;
            //         }
    
            //         self.addedFiles(Object.values(uploadedFiles));
            //     });
            // }

        }


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
                url: arches.urls.graph_nodes(OBSERVATIONS_GRAPH_ID),
                success: function (response) {
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
                }
            });
        };

        this.buttonFOO = function() {
            console.log(self, params)
            // params.node.loading = ko.observable(true)


            // self.createdResources(
            //     self.parsedFileData.removeAll()
            // );



            $.ajax({
                dataType: "json",
                type: 'POST',
                contentType: "application/json",
                data: JSON.stringify({
                    'foobar': true,
                    'foo': self.parsedFileData(),
                }),
                url: arches.urls.api_external_foobar(graphid=OBSERVATIONS_GRAPH_ID),
                success: function(response) {
                    console.log(response)

                    self.createdResources(
                        self.parsedFileData.removeAll()
                    );
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