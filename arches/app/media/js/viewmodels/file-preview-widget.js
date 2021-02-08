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
                data: JSON.stringify({
                    graph_ids: [ arches.resources[1]['graphid'] ],
                    data: data,
                }),
                success: function (response) {
                    console.log('!!!', response)
                }
            });
        };



        this.foo = function(barfoo) {

            console.log("SHS", barfoo, arches)
            // self.callMe()


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
    
                        barfoo.push({
                            'file': file,
                            'data': {
                                columnNames: results['data'].shift(),
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