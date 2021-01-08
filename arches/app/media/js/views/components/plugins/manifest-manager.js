define([
    'knockout',
    'dropzone',
    'uuid',
    'arches',
    'views/components/iiif-viewer',
    'bindings/dropzone'
], function (ko, Dropzone, uuid, arches, IIIFViewerViewmodel) {
    return ko.components.register('manifest-manager', {
        viewModel: function(params) {
            var self = this;

            this.unsupportedImageTypes = ['tif', 'tiff', 'vnd.adobe.photoshop'];

            this.imagesForUpload = ko.observableArray([]);
            this.canvasesForDeletion = ko.observableArray([]);
            //this.metadataToAdd = ko.observableArray([]);
            //this.metadataToRemove = ko.observableArray([]);
            this.metaDataLabel = ko.observable('')
            this.metaDataValues = ko.observable('')

            this.addCanvas = function(canvas) { //the function name needs to be better
                self.canvasesForDeletion.push(canvas);
                self.canvas(canvas.images[0].resource.service['@id'])
            };

            this.removeCanvas = function(canvas) { //the function name needs to be better
                self.canvasesForDeletion.remove(canvas);
                self.canvas(canvas.images[0].resource.service['@id'])
            };

            IIIFViewerViewmodel.apply(this, [params]);

            this.isManifestDirty = ko.computed(function() {
                return ((ko.unwrap(self.manifestName) !== self.origManifestName) ||
                        (ko.unwrap(self.manifestDescription) !== self.origManifestDescription) ||
                        ((ko.unwrap(self.metaDataLabel) !== '') && (ko.unwrap(self.metaDataValues) !== ''))
                        );
            });

            this.isCanvasDirty = ko.computed(function() {
                return (ko.unwrap(self.canvasLabel) !== self.origCanvasLabel);
            });

            this.uniqueId = uuid.generate();
            this.uniqueidClass = ko.computed(function() {
                return "unique_id_" + self.uniqueId;
            });

            this.formData = new FormData();

            this.addAllCanvases = function() {
                self.canvases().forEach(function(canvas){
                    if (self.canvasesForDeletion().indexOf(canvas) < 0) {
                        self.canvasesForDeletion.push(canvas);
                    }
                });
            };

            this.clearCanvasSelection = function() {
                self.canvasesForDeletion([]);
            };

            this.removeFile = function(file){
                self.imagesForUpload.remove(file);
            };

            this.reset = function() {
                self.formData.delete("files");
                self.formData = new FormData();
                self.imagesForUpload.removeAll();
                self.metaDataLabel('');
                self.metaDataValues('');
                self.manifestName(self.origManifestName);
                self.manifestDescription(self.origManifestDescription);
                self.canvasLabel(self.origCanvasLabel);
                if (self.dropzone) {
                    self.dropzone.removeAllFiles(true);
                }
            };

            this.submitToManifest = function(){
                $.ajax({
                    type: "POST",
                    url: arches.urls.manifest_manager,
                    data: self.formData,
                    cache: false,
                    processData: false,
                    contentType: false,
                    success: function(response) {
                        self.reset();
                        self.manifest(response.url);
                        self.getManifestData();
                        console.log('Submitted');
                    },
                    error: function(response) {
                        self.reset();
                        console.log(response);
                        console.log("Failed");
                    }
                })
            };

            this.deleteCanvases = function() {
                self.formData.append("manifest", ko.unwrap(self.manifest));
                self.formData.append("selected_canvases", JSON.stringify(ko.unwrap(self.canvasesForDeletion)));
                self.submitToManifest();
            };

            this.deleteManifest = function(){
                self.formData.append("manifest", ko.unwrap(self.manifest));
                $.ajax({
                    type: "DELETE",
                    url: arches.urls.manifest_manager,
                    data: JSON.stringify({"manifest": ko.unwrap(self.manifest)}),
                    cache: false,
                    processData: false,
                    contentType: false,
                    success: function(response) {
                        self.reset();
                        self.toggleManifestEditor();
                        self.manifestData(null);
                        self.manifest(null);
                        self.canvas(null);
                        self.manifestName(null);
                        self.manifestDescription(null);
                        self.expandGallery(true);
                        console.log('Deleted');
                    },
                    error: function(response) {
                        self.reset();
                        console.log("Failed to Delete");
                    }
                })
            };

            this.createManifest = function(fileList){
                Array.from(fileList).forEach(function(file) {
                    self.formData.append("files", file, file.name);
                    self.imagesForUpload.push(file);})
                self.formData.append("manifest_title", ko.unwrap(self.manifestName));
                self.formData.append("manifest_description", ko.unwrap(self.manifestDescription));
                self.formData.append("operation", "create")
                self.submitToManifest();
            };

            this.addFiles = function(fileList) {
                Array.from(fileList).forEach(function(file) {
                    self.formData.append("files", file, file.name);
                    self.imagesForUpload.push(file);})
                self.updateManifest();
            };

            this.updateManifest = function() {
                self.formData.append("manifest_title", ko.unwrap(self.manifestName));
                self.formData.append("manifest_description", ko.unwrap(self.manifestDescription));
                self.formData.append("manifest", ko.unwrap(self.manifest));
                self.formData.append("canvas_label", ko.unwrap(self.canvasLabel)); //new label for canvas
                self.formData.append("canvas_id", ko.unwrap(self.canvas)); //canvas id for label change
                self.formData.append("metadata_label", ko.unwrap(self.metaDataLabel));
                self.formData.append("metadata_values", ko.unwrap(self.metaDataValues));
                self.submitToManifest();
            };

            this.dropzoneOptions4create = {
                url: "arches.urls.root",
                dictDefaultMessage: '',
                autoProcessQueue: false,
                uploadMultiple: true,
                autoQueue: false,
                clickable: ".fileinput-create-button." + this.uniqueidClass(),
                previewsContainer: '#hidden-dz-create-previews',
                init: function() {
                    self.dropzone = this;
                    this.on("addedfiles", self.createManifest); 
                    this.on("error", function(file, error) {
                        file.error = error;
                        self.imagessForUpload.valueHasMutated();
                    });    
                }
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
                        self.imagessForUpload.valueHasMutated();
                    });    
                }
            };
        },
        template: { require: 'text!templates/views/components/plugins/manifest-manager.htm' }
    })
});