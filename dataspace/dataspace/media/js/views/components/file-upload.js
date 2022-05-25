define([
    'knockout',
    'uuid',
    'bindings/dropzone'
], function(ko, uuid) {
    /**
    * knockout components namespace used in arches
    * @external "ko.components"
    * @see http://knockoutjs.com/documentation/component-binding.html
    */

    /**
    * registers a file-upload component
    * @function external:"ko.components".file-upload
    * @param {object} params
    */
    return ko.components.register('file-upload', {
        viewModel: function(params) {
            this.acceptedFiles = ko.observableArray([]);
            var self = this;
            this.uniqueId = uuid.generate();
            this.uniqueidClass = ko.computed(function() {
                return "unique_id_" + self.uniqueId;
            });
            this.addFiles = function(val){
                console.log('got files');
                console.log(val);
            };
            this.dropzoneOptions = {
                url: "arches.urls.root",
                dictDefaultMessage: '',
                autoProcessQueue: false,
                uploadMultiple: true,
                autoQueue: false,
                clickable: ".fileinput-button." + this.uniqueidClass(),
                previewsContainer: '#hidden-dz-previews',
                init: function() {
                    self.dropzone = this;
                    this.on("addedfiles", self.addFiles);
                    this.on("error", function(file, error) {
                        file.error = error;
                    });    
                }
            };
        },
        template: {
            require: 'text!templates/views/components/file-upload.htm'
        }
    });
});
