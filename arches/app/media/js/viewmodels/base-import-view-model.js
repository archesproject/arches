define(['jquery', 'knockout', 'uuid', 'arches', 'js-cookie'], function($, ko, uuid, arches, Cookies) {
    /**
    * A base viewmodel for import modules
    *
    * @constructor
    * @name ImportModuleViewModel
    *
    * @param  {string} params
    */
    const ImportModuleViewModel = function() {
        const self = this;
        this.transactionId = uuid.generate();
        this.fileAdded = ko.observable(false);
        this.fileInfo = ko.observable({name:"", size:""});
        this.formData = new window.FormData();
        this.uniqueidClass = ko.computed(function() {
            return "unique_id_" + uuid.generate();
        });

        this.addFile = function(file){
            self.loading(true);
            self.fileInfo({name: file.name, size: file.size});
            self.formData.append('file', file, file.name);
            self.submit('read').then(function(){
                self.fileAdded(true);
                self.loading(false);
            }).catch(function(err) {    
                // eslint-disable-next-line no-console
                console.log(err);
                self.loading(false);
            });
        };

        this.submit = function(action) {
            self.formData.append('action', action);
            self.formData.append('transaction_id', self.transactionId);
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
