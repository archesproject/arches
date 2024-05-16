define([
    'knockout',
    'knockout-mapping',
    'jquery',
    'dropzone',
    'uuid',
    'arches',
    'viewmodels/alert-json',
    'views/components/iiif-viewer',
    'templates/views/components/plugins/manifest-manager.htm',
    'bindings/dropzone'
], function(ko, koMapping, $, Dropzone, uuid, arches, JsonErrorAlertViewModel, IIIFViewerViewmodel, manifestManagerTemplate) {
    return ko.components.register('manifest-manager', {
        viewModel: function(params) {
            var self = this;
             
            this.transactionId = params.transactionId || uuid.generate();
            this.canvasesForDeletion = ko.observableArray([]);
            this.metadataLabel = ko.observable('');
            this.metadataValues = ko.observable('');
            this.mainMenu = ko.observable(true);

            // params.shouldShowEditService is deprecated, but retained for backward compatibility for other projects that may have used it.  Use params.shouldShowSelectService instead.
            this.shouldShowSelectService = params.shouldShowSelectService || params.shouldShowEditService || ko.observable(true);
            this.selectService = ko.observable(false);
            
            this.shouldShowCreateService = params.shouldShowCreateService || ko.observable(true);
            this.createService = ko.observable(true);

            this.remoteManifest = ko.observable(true);
            this.alert = params.alert || ko.observable(); 
            this.addCanvas = function(canvas) { //the function name needs to be better
                self.canvasesForDeletion.push(canvas);
                self.canvas(canvas.images[0].resource.service['@id']);
            };

            this.removeCanvas = function(canvas) { //the function name needs to be better
                self.canvasesForDeletion.remove(canvas);
                self.canvas(canvas.images[0].resource.service['@id']);
            };

            IIIFViewerViewmodel.apply(this, [{...params, renderContext: params?.renderContext ? params.renderContext: 'manifestManager'}]);
            this.showTabs(false);
            this.mainMenu.subscribe(function(val){
                val || self.showTabs(true);
            });

            if(this.renderContext() == "manifest-workflow"){
                this.showModeSelector(false);
            }
            this.isManifestDirty = ko.computed(function() {
                return ((ko.unwrap(self.manifestName) !== self.origManifestName) ||
                        (ko.unwrap(self.manifestDescription) !== self.origManifestDescription) ||
                        (ko.unwrap(self.manifestAttribution) !== self.origManifestAttribution) ||
                        (ko.unwrap(self.manifestLogo) !== self.origManifestLogo) ||
                        (ko.unwrap(self.metadataLabel)) ||
                        (ko.unwrap(self.metadataValues)) ||
                        (koMapping.toJSON(self.manifestMetadata) !== self.origManifestMetadata)
                );});

            this.isCanvasDirty = ko.computed(function() {
                return !self.compareMode() && (self.canvasLabel() !== self.origCanvasLabel());
            });

            this.uniqueId = uuid.generate();
            this.uniqueidClass = ko.computed(function() {
                return "unique_id_" + self.uniqueId;
            });

            this.formData = new window.FormData();

            this.stagedMetadata = ko.computed(function(){
                var res = {label: self.metadataLabel(), value: self.metadataValues()};
                return res;
            });

            this.updateMetadata = function(){
                if (!!self.metadataLabel() || !!self.metadataValues()) {
                    this.manifestMetadata.unshift(koMapping.fromJS(this.stagedMetadata()));
                }
                self.metadataLabel(null);
                self.metadataValues(null);
            };

            this.removeMetadata = function(val) {
                this.manifestMetadata.remove(val);
            };

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


            this.reset = function() {
                self.formData.delete("files");
                self.formData = new window.FormData();
                self.clearCanvasSelection();
                self.metadataLabel('');
                self.metadataValues('');
                self.manifestName(self.origManifestName);
                self.manifestAttribution(self.origManifestAttribution);
                self.manifestLogo(self.origManifestLogo);
                self.manifestDescription(self.origManifestDescription);
                self.canvasLabel(self.origCanvasLabel());
                if (self.origManifestMetadata) {
                    self.manifestMetadata.removeAll();
                    JSON.parse(self.origManifestMetadata).forEach(function(entry){
                        self.manifestMetadata.push(koMapping.fromJS(entry));
                    });
                }
                if (self.dropzone) {
                    self.dropzone.removeAllFiles(true);
                }
            };

            this.submitToManifest = function(onSuccess, onError){
                if (params.manifestManagerFormData) {
                    params.manifestManagerFormData(self.formData);
                }
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
                        if (onSuccess) {
                            onSuccess();
                        }
                    },
                    error: function(response) {
                        self.reset();
                        // eslint-disable-next-line no-console
                        console.log("Failed to save manifest");
                        self.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                        if (onError) {
                            onError();
                        }
                    }
                });
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
                    success: function() {
                        self.reset();
                        self.toggleManifestEditor();
                        self.manifestData(null);
                        self.manifest(null);
                        self.canvas(null);
                        self.manifestName(null);
                        self.manifestDescription(null);
                        self.manifestAttribution(null);
                        self.expandGallery(true);
                        self.mainMenu(true);
                        self.activeTab(undefined);
                    },
                    error: function(response) {
                        self.reset();
                        // eslint-disable-next-line no-console
                        console.log("Failed to delete manifest");
                        self.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                    }
                });
            };

            this.createManifest = function(fileList){
                Array.from(fileList).forEach(function(file) {
                    self.formData.append("files", file, file.name);
                });
                self.formData.append("manifest_title", ko.unwrap(self.manifestName));
                self.formData.append("manifest_description", ko.unwrap(self.manifestDescription));
                self.formData.append("operation", "create");
                self.formData.append("transaction_id", self.transactionId);
                var onSuccess = function() {
                    self.activeTab('manifest');
                    self.mainMenu(false);
                };
                var onError = function() {
                    self.mainMenu(true);
                    self.activeTab(undefined);
                };
                self.submitToManifest(onSuccess, onError);
            };

            this.addFiles = function(fileList) {
                Array.from(fileList).forEach(function(file) {
                    self.formData.append("files", file, file.name);
                });
                self.updateManifest();
            };

            this.updateManifest = function() {
                self.updateMetadata();
                self.formData.append("manifest_title", ko.unwrap(self.manifestName));
                self.formData.append("manifest_description", ko.unwrap(self.manifestDescription));
                self.formData.append("manifest_attribution", ko.unwrap(self.manifestAttribution));
                self.formData.append("manifest_logo", ko.unwrap(self.manifestLogo));
                self.formData.append("manifest", ko.unwrap(self.manifest));
                self.formData.append("canvas_label", ko.unwrap(self.canvasLabel) ?? ''); //new label for canvas
                self.formData.append("canvas_id", ko.unwrap(self.canvas)); //canvas id for label change
                self.formData.append("metadata", JSON.stringify(koMapping.toJS(self.manifestMetadata)));
                self.updateCanvas = false;
                self.submitToManifest();
            };

            this.manifest.subscribe(function(val){
                self.getManifestData(val);
                self.mainMenu(false);
            });

            this.manifestData.subscribe(function(manifestData) {
                if (manifestData) {
                    self.selectCanvas(manifestData.sequences[0].canvases[0]);
                }
                if (params.manifestData && ko.isObservable(params.manifestData)) {
                    params.manifestData(manifestData);
                }
            });

            this.manifest.subscribe(function(){
                if (self.manifest() && self.manifest().charAt(0) == '/') {
                    self.remoteManifest(false);
                }
                else {
                    self.remoteManifest(true);
                }
                self.hideSidePanel();
            }); 
          
            this.dropzoneOptions4create = {
                url: "arches.urls.root",
                dictDefaultMessage: '',
                autoProcessQueue: false,
                uploadMultiple: true,
                acceptedFiles: ["image/jpeg", "image/png", "image/tiff"].join(','),
                autoQueue: false,
                clickable: ".fileinput-create-button." + this.uniqueidClass(),
                previewsContainer: '#hidden-dz-create-previews',
                init: function() {
                    self.dropzone = this;
                    this.on("addedfiles", self.createManifest); 
                    this.on("error", function(file, error) {
                        file.error = error;
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
                    });    
                }
            };
        },
        template: manifestManagerTemplate,
    });
});