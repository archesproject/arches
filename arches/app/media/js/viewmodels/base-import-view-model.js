define(['jquery', 'knockout', 'uuid', 'arches', 'js-cookie'], function($, ko, uuid, arches, Cookies) {
    /**
    * A base viewmodel for import modules
    *
    * @constructor
    * @name ImportModuleViewModel
    *
    * @param  {string} params
    */
    const ImportModuleViewModel = function(params) {
        const self = this;
        this.alert = params.alert;
        this.fileAdded = ko.observable(false);
        this.fileInfo = ko.observable({name:"", size:""});
        this.formData = new window.FormData();
        this.uniqueidClass = ko.computed(function() {
            return "unique_id_" + uuid.generate();
        });
        this.response = ko.observable();
        this.validationError = ko.observable();

        this.submit = function(action) {
            self.formData.append('action', action);
            if (action === 'start') {
                self.loadId = uuid.generate();
            }
            if (action === 'read') {
                self.formData.append('async', true);
            }
            self.formData.append('load_id', self.loadId);
            self.formData.append('module', this.moduleId);
            return fetch(arches.urls.etl_manager, {
                method: 'POST',
                body: self.formData,
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                }
            });
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
    };
    return ImportModuleViewModel;
});
