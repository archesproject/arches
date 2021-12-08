define([
    'knockout',
    'knockout-mapping',
    'jquery',
    'dropzone',
    'uuid',
    'arches',
    'bindings/dropzone'
], function(ko, koMapping, $, dropzone, uuid, arches) {
    return ko.components.register('import-single-csv', {
        viewModel: function(params) {
            self = this;

            this.loading = params.loading;
            this.loading(false);
            this.fileAdded = ko.observable(false);

            this.uniqueId = uuid.generate();
            this.uniqueidClass = ko.computed(function() {
                return "unique_id_" + self.uniqueId;
            });

            this.addFile = function(){
                console.log("A file added");
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
        },
        template: { require: 'text!templates/views/components/etlmodules/import-single-csv.htm' }
    });
});