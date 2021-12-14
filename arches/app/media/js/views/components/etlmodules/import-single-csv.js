define([
    'knockout',
    'knockout-mapping',
    'jquery',
    'dropzone',
    'uuid',
    'arches',
    'bindings/dropzone',
    'bindings/datatable'
], function(ko, koMapping, $, dropzone, uuid, arches) {
    return ko.components.register('import-single-csv', {
        viewModel: function(params) {
            self = this;
            this.loading = params.loading;
            this.loading(true);

            this.fileAdded = ko.observable(false);
            this.formData = new window.FormData();
            this.transaction_id = uuid.generate();
            this.uniqueId = uuid.generate();
            this.uniqueidClass = ko.computed(function() {
                return "unique_id_" + self.uniqueId;
            });

            this.createTableConfig = function(col) {
                return {
                    paging: false,
                    searching: false,
                    scrollCollapse: true,
                    info: false,
                    // columnDefs: [{
                    //     orderable: false,
                    //     targets: -1,
                    // }],
                    columns: Array(col).fill(null)
                };
            };

            this.hasHeaders = ko.observable(true);
            this.csvArray = ko.observableArray();
            this.headers = ko.observableArray();
            this.csvBody = ko.observableArray();
            this.numberOfCol = ko.observable();

            this.hasHeaders.subscribe(function(val){
                if (val) {
                    self.headers(self.csvArray()[0]);
                    self.csvBody(self.csvArray().slice(1));
                } else {
                    self.headers(null);
                    self.csvBody(self.csvArray());
                };
            })

            this.csvArray.subscribe(function(val){
                self.numberOfCol(val[0].length);
                if (self.hasHeaders()) {
                    self.headers(val[0]);
                    self.csvBody(val.slice(1));
                } else {
                    self.headers(null);
                    self.csvBody(val);
                }
                self.previewTableConfig = self.createTableConfig(self.numberOfCol())
            });

            this.addFile = function(file){
                self.loading(true);;
                console.log(file)
                self.formData.append('file', file, file.name);
                self.submit('add').then(function(response){
                //     if (response.ok) {
                //         self.fileAdded(true);
                //         return response.json;
                //     }
                // }).then(function(response){
                    self.csvArray(response.csv)
                    self.fileAdded(true);
                    self.loading(false);;
                }).catch(function(err) {
                    self.loading(false);
                })
            };

            this.submit = function(action) {
                self.formData.append('action', action);
                self.formData.append('transaction_id', self.transaction_id);
                self.formData.append('module','import-single-csv')
                return $.ajax({
                    type: "POST",
                    url: arches.urls.etl_manager,
                    data: self.formData,
                    cache: false,
                    processData: false,
                    contentType: false,
                });
                // return window.fetch(arches.urls.etl_manager, {
                //     method: 'POST',
                //     credentials: 'include',
                //     body: self.formData,
                //     headers: {
                //         'Content-Type': 'application/json'
                //     },
                // });
            };

            this.dropzoneOptions = {
                url: "arches.urls.root",
                dictDefaultMessage: '',
                autoProcessQueue: false,
                uploadMultiple: false,
                // acceptedFiles: ["text/csv"],
                autoQueue: false,
                clickable: ".fileinput-button." + this.uniqueidClass(),
                previewsContainer: '#hidden-dz-previews',
                init: function() {
                    self.dropzone = this;
                    this.on("addedfile", self.addFile); 
                    this.on("error", function(file, error) {
                        file.error = error;
                    });    
                }
            };
            this.loading(false);
        },
        template: { require: 'text!templates/views/components/etlmodules/import-single-csv.htm' }
    });
});