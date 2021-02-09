define([
    'jquery',
    'knockout',
    'underscore',
    'arches',
    'dropzone',
    'uuid',
    'papaparse',
    'viewmodels/widget',
    'bindings/dropzone'
], function($, ko, _, arches, Dropzone, uuid, Papa, WidgetViewModel) {
    /**
     * A viewmodel used for viewing and uploading external resource data 
     *
     * @constructor
     * @name ExternalResourceDataViewModel
     *
     * @param  {string} params - a configuration object
     */




    OBSERVATIONS_CSV_COLUMN_NAME_TO_NODE_IDS = {
        'ObserverName*': "0da1fe5e-04fd-11eb-9978-02e99e44e93e", 
        'ObserverContact*': "12bd77bb-04fd-11eb-9978-02e99e44e93e", 
        'ObserverAffiliation': "21f08600-04fd-11eb-9978-02e99e44e93e", 
        'SpeciesName*': "fca0475a-04fc-11eb-9978-02e99e44e93e", 
        'Positive Observation': "abdaf060-37ef-11eb-a206-acde48001122", 
        'SpDetermine': "", 
        'ID_Confidence': "", 
        'ObservationDate*': "d7628ae4-3f2f-11eb-a2e2-73ab08a728ea", 
        'NoPlantsObsvd*': "", 
        'Phenology': "347a1388-3be2-11eb-8a94-acde48001122", 
        'Collection': "", 
        'NoAnimalsObs': "", 
        'AnimalAgeClass': "fd0dd812-3be1-11eb-8a94-acde48001122", 
        'AnimalSiteUse*': "fd0dd6b4-3be1-11eb-8a94-acde48001122", 
        'AnimalBehavior*': "fd0dd5c4-3be1-11eb-8a94-acde48001122", 
        'AnimalDetectionMethod*': "fd0dd768-3be1-11eb-8a94-acde48001122", 
        'LocationDescription': "e9f6767e-033f-11eb-9978-02e99e44e93e", 
        'X_Coordinate*': "", 
        'Y_Coordinate*': "", 
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
        params.configKeys = ['acceptedFiles', 'maxFilesize', 'maxFiles'];
        WidgetViewModel.apply(this, [params]);
        
        var self = this;

        this.unique_id = uuid.generate();
        this.uniqueidClass = ko.computed(function() {
            return "unique_id_" + self.unique_id;
        });

        this.filter = ko.observable("");

        this.uploadMultiple = ko.observable(true);
        this.addedFiles = ko.observableArray();
        this.selectedFile = ko.observable(self.addedFiles()[0]);


        this.resourceModelNodes = ko.observable({});


        this.barfoo = ko.observable([]);
        this.barfoo.subscribe(function(barfoo) {
            self.foo(barfoo)
        });


        // console.log("SHS", arches, arches.resources[1]['graphid'])




        // // WORKING
        // $.ajax({
        //     dataType: "json",
        //     url: arches.urls.graph + arches.resources[1]['graphid'] + '/nodes',
        //     success: function (response) {
        //         console.log('!!!', response)
        //     }
        // });



        this.callMe = function(data) {
            $.ajax({
                dataType: "json",
                url: arches.urls.resource + '/data/',
                method: 'POST',
                data: {
                    graph_ids: JSON.stringify([ arches.resources[1]['graphid'] ]),
                    barfoo: JSON.stringify(self.barfoo()),

                },
                success: function (response) {
                    console.log('!!!', response)
                }
            });
        };


        this.fetchResourceModelNodes = function() {
            $.ajax({
                dataType: "json",
                url: arches.urls.graph_nodes(arches.resources[1]['graphid']),
                success: function (response) {
                    self.resourceModelNodes(response);
                }
            });
        };

        this.fetchResourceModelNodes();



        this.foo = function(barfoo) {

            barfoo.forEach(function(barfooObj) {

            });

            self.callMe()
            
            console.log("___", self)


            // Object.values(bar).forEach(function(foobar) {
            //     console.log(foobar);
            // })
        };




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

        this.parseCSVFile = function(file) {
            Papa.parse(file, {
                worker: true,
                complete: function(results) {
                    if (results.errors.length) {
                        console.log("ERROR ALERT HERE")
                    }
                    else {
                        var barfoo = self.barfoo();

                        var columnNames = results['data'].shift();

                        barfoo.push({
                            file: file,
                            data: {
                                node_ids: columnNames.map(function(columnName) {
                                    return OBSERVATIONS_CSV_COLUMN_NAME_TO_NODE_IDS[columnName];
                                }),  
                                rows: results['data'],
                            },
                        });
    
                        self.barfoo(barfoo);

                        self.addedFiles.push(file);





                        // self.barfoo.push({
                        //     'file': file,
                        //     'data': {
                        //         columnsNames: results['data'].shift(),
                        //         rows: results['data'],
                        //     },
                        // });
                    }
                },
            });
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
    };

    return ExternalResourceDataViewModel;
});