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

        this.submit = async function(action, formData) {
            let payload = formData || self.formData;
            payload.append('action', action);
            if (['start', 'read'].includes(action)) {
                if (!self.loadId) {
                    self.loadId = uuid.generate();
                }
            }
            payload.append('load_id', self.loadId);
            payload.append('module', this.moduleId);
            return fetch(arches.urls.etl_manager, {
                method: 'POST',
                body: payload,
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
