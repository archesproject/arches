define([
    'knockout',
    'knockout-mapping',
    'uuid',
    'arches',
    'utils/resource',
    'utils/physical-thing',
    'viewmodels/alert-json',
    'views/components/iiif-viewer',
    'bindings/dropzone'
], function(ko, koMapping, uuid, arches, resourceUtils, physicalThingUtils, JsonErrorAlertViewModel, IIIFViewerViewmodel) {
    return ko.components.register('select-dataset-files-step', {
        viewModel: function(params) {
            IIIFViewerViewmodel.apply(this, [params]);
            var defaultColor;
            var self = this;
            const physicalThingPartNameNodeId = "3e541cc6-859b-11ea-97eb-acde48001122";
            const physicalThingPartNodeGroupId = "fec59582-8593-11ea-97eb-acde48001122";
            const physicalThingPartAnnotationNodeId = "97c30c42-8594-11ea-97eb-acde48001122";
            const physicalThingPartNodeId = "b240c366-8594-11ea-97eb-acde48001122";
            const projectInfo = params.projectInfo;
            const observationInfo = params.observationInfo;
            const observationResourceId = params.observationInfo.observationInstanceId;
            const observationGraphId = "615b11ee-c457-11e9-910c-a4d18cec433a";
            const digitalResourceGraphId = "707cbd78-ca7a-11e9-990b-a4d18cec433a";
            const datasetNameNodeGroupId = "d2fdae3d-ca7a-11e9-ad84-a4d18cec433a";
            const datasetNameNodeId = "d2fdc2fa-ca7a-11e9-8ffb-a4d18cec433a";
            const datasetFileNodeGroupId = "7c486328-d380-11e9-b88e-a4d18cec433a";
            const datasetFileNodeId = "7c486328-d380-11e9-b88e-a4d18cec433a";
            const rendererLookup = {                
                
                "3526790a-c73d-4558-b29d-98f574c91e61": {name: "Bruker Artax x-ray fluorescence spectrometer", renderer: "xrf-reader", rendererid: "31be40ae-dbe6-4f41-9c13-1964d7d17042"},
                "UV-Vis-NIR reflection": {name: "UV-Vis-NIR reflection", renderer: "uv_vis-reader", rendererid: "baf93c49-d215-4fcb-a422-dc1d629664ee"},
		    "MIR":{name: "MIR", renderer: "mir-reader", rendererid: "a891e5ad-5562-4b7b-9978-1fe33c9f65e8"},
                "3365c1bf-070d-4a8e-b859-52dec6876c1d": {name: "ASD HiRes FieldSpec4", renderer: "fors-renderer", rendererid: "88dccb59-14e3-4445-8f1b-07f0470b38bb"},
		    "73717b33-1235-44a1-8acb-63c97a5c1157": {name: "Renishaw inVia Raman microscope using a 785 nm laser", renderer: "raman-reader", rendererid: "94fa1720-6773-4f99-b49b-4ea0926b3933"},

		    //"csv": {rendererid: "a1ed1521-f358-452c-bab8-bcd8712c0f18", renderer: "csv-reader"},
                "image": {rendererid: "5e05aa2e-5db0-4922-8938-b4d2b7919733", renderer: "imagereader"},
                "pdf": {rendererid: "09dec059-1ee8-4fbd-85dd-c0ab0428aa94", renderer: "pdfreader"},
            };

            this.annotationNodeId = "b3e171ae-1d9d-11eb-a29f-024e0d439fdb";
            this.samplingActivityGraphId = "03357848-1d9d-11eb-a29f-024e0d439fdb";
            this.selectedAnnotationTile = ko.observable();
            this.selectedPart = ko.observable();
            this.partFilter = ko.observable("");
            this.annotations = ko.observableArray([]);
            this.selectedPartObservationId = ko.observable();
            this.parts = ko.observableArray([]);
            this.uniqueId = uuid.generate();
            this.observationReferenceTileId = ko.observable();
            this.formData = new window.FormData();
            this.physicalThing = projectInfo.physicalThing;
            this.uniqueidClass = ko.computed(function() {
                return "unique_id_" + self.uniqueId;
            });
            this.firstLoad = true;
            this.mainMenu = ko.observable(true);
            this.files = ko.observableArray([]);
            this.initialValue = params.form.savedData() || undefined;
            this.snapshot = undefined;
            this.savingMessage = ko.observable();
            this.savingFile = ko.observable(false);

            this.selectedPartHasCurrentObservation = ko.computed(() => {
                if(!self.selectedPart()?.observationResourceId){
                    return true;
                } else {
                    return self.selectedPart().observationResourceId == observationResourceId;
                }
            })

            this.switchCanvas = function(canvasId){
                var canvas = self.canvases().find(c => c.images[0].resource.service['@id'] === canvasId);
                if (canvas) {
                    self.canvasClick(canvas);              
                }
            };

            this.highlightAnnotation = function(){
                if (self.map()) {
                    self.map().eachLayer(function(layer){
                        if (layer.eachLayer) {
                            layer.eachLayer(function(features){
                                if (features.eachLayer) {
                                    features.eachLayer(function(feature) {
                                        if (!defaultColor) {
                                            defaultColor = feature.feature.properties.color;
                                        }
                                        if (self.selectedAnnotationTile().tileid === feature.feature.properties.tileId) {
                                            feature.setStyle({color: '#BCFE2B', fillColor: '#BCFE2B'});
                                        } else {
                                            feature.setStyle({color: defaultColor, fillColor: defaultColor});
                                        }
                                    });
                                }
                            });
                        }
                    });
                } 
            };

            this.getAnnotationProperty = function(tile, property){
                return tile.data[physicalThingPartAnnotationNodeId].features[0].properties[property];
            };

            this.selectedPart.subscribe(async (data) => {
                self.selectedPartObservationId(self.selectedPart().observationResourceId);

                self.annotations([data]);
                if (self.annotations().length) {
                    self.selectedAnnotationTile(self.annotations()[0]);
                    if (self.manifest() !== self.getAnnotationProperty(self.selectedAnnotationTile(), "manifest")) {
                        self.manifest(self.getAnnotationProperty(self.selectedAnnotationTile(), "manifest"));
                        self.getManifestData();
                    }
                    self.switchCanvas(self.getAnnotationProperty(self.selectedAnnotationTile(), "canvas"));
                }
            });

            this.canvas.subscribe(function(val){
                if (typeof val === "string") {
                    let annotationCanvas = self.getAnnotationProperty(self.selectedAnnotationTile(), "canvas");
                    if (annotationCanvas === val || self.firstLoad === true) {
                        self.switchCanvas(annotationCanvas);
                        self.firstLoad = false;
                    }
                }
            });

            this.addFiles = function(fileList) {
                Array.from(fileList).forEach(function(file) {
                    self.files.push(file);
                });
                if (self.files()) {
                    self.mainMenu(false);
                    self.activeTab('dataset');
                    self.annotationNodes.valueHasMutated();
                }
            };

            this.addFileToPart = (file) => {
                if(self.selectedPart() && self.selectedPartHasCurrentObservation()) {
                    file.tileId = ko.observable();
                    self.selectedPart().datasetFiles.push(file);
                    self.parts.valueHasMutated();
                    self.files.remove(file);
                    
                }
            }

            this.removeFileFromPart = (file) => {
                if(self.selectedPart() && self.selectedPartHasCurrentObservation()) {
                    self.selectedPart().datasetFiles.remove(file);
                    self.files.push(file);
                }
            }

            this.saveDatasetName = async (part) => {

                //Tile structure for the Digital Resource 'Name' nodegroup
                const nameTemplate = {
                    "tileid": part.nameTileId() || "",
                    "data": {
                        "d2fdc2fa-ca7a-11e9-8ffb-a4d18cec433a": null,
                        "d2fdc0d4-ca7a-11e9-95cf-a4d18cec433a": ["8f40c740-3c02-4839-b1a4-f1460823a9fe"],
                        "d2fdb92b-ca7a-11e9-af41-a4d18cec433a": ["bc35776b-996f-4fc1-bd25-9f6432c1f349"],
                        "d2fdbc38-ca7a-11e9-a31a-a4d18cec433a": null,
                        "d2fdbeb8-ca7a-11e9-a294-a4d18cec433a": null
                    },
                    "nodegroup_id": datasetNameNodeGroupId,
                    "parenttile_id": null,
                    "resourceinstance_id": ko.unwrap(part.datasetId),
                    "sortorder": 0,
                    "tiles": {},
                    "transaction_id": params.form.workflowId
                };

                nameTemplate.data[datasetNameNodeId] = part.calcDatasetName();

                const tile = await window.fetch(arches.urls.api_tiles(part.datasetId() || ""), {
                    method: 'POST',
                    credentials: 'include',
                    body: JSON.stringify(nameTemplate),
                    headers: {
                        'Content-Type': 'application/json'
                    },
                });

                if(tile.ok){
                    const json = await tile.json();
                    part.nameDirty(false);
                    return {
                        resourceId: json?.resourceinstance_id, 
                        tileId: json?.tileid
                    };
                }
            };

            this.createObservationCrossReferences = async () => {
                const recordedValueNodeId = "dd596aae-c457-11e9-956b-a4d18cec433a";
                const tileid = self.observationReferenceTileId() || "";
                const digitalReferenceTile = {
                    "tileid": self.observationReferenceTileId() || "",
                    "data": {},
                    "nodegroup_id": recordedValueNodeId,
                    "parenttile_id": null,
                    "resourceinstance_id": observationResourceId,
                    "sortorder": 1,
                    "tiles": {},
                    "transaction_id": params.form.workflowId
                };

                const getPartObservationId = async (part) => {
                    if(part.datasetId()) {
                        const selectedDatasetCrossReferences = await (await window.fetch(`${arches.urls.related_resources}${part.datasetId()}`)).json();
                        const relatedObservation = selectedDatasetCrossReferences?.related_resources?.related_resources?.filter(x => x?.graph_id == observationGraphId);
                        part.observationResourceId = relatedObservation?.[0]?.resourceinstanceid;
                        if(part.datasetId() == self.selectedPart().datasetId()){
                            self.selectedPart.valueHasMutated()
                        }
                    }
                };

                await Promise.all(self.parts().map(getPartObservationId));
                
                digitalReferenceTile.data[recordedValueNodeId] = 
                    self.parts().filter((part) => {
                        return ((part.datasetId() && (!part.observationResourceId || part.observationResourceId === observationResourceId)) ? true : false); // observation reference already exists
                    }).map(part => { 
                        return {
                            "resourceId": part.datasetId(),
                            "ontologyProperty": "",
                            "inverseOntologyProperty": ""
                        };
                    });

                const result = await window.fetch(arches.urls.api_tiles(tileid), {
                    method: 'POST',
                    credentials: 'include',
                    body: JSON.stringify(digitalReferenceTile),
                    headers: {
                        'Content-Type': 'application/json'
                    },
                });

                if(result.ok){
                    const json = await result.json();
                    self.observationReferenceTileId(json?.tileid);
                    return json;
                }
            };

            // this.removeDatasetFiles = async (part) => {
            //     const savedDatasetFiles = self.snapshot?.parts.find(p => p.datasetId === part.datasetId()).datasetFiles
            //     if (savedDatasetFiles) {
            //         const currentTileIds = part.datasetFiles().map(val => ko.unwrap(val.tileId)) 
            //         const savedTileIds = savedDatasetFiles.map(val => val.tileId) 
            //         const tilesToDelete = savedTileIds.filter(tileid => !currentTileIds.includes(tileid));
            //         tilesToDelete.forEach(async (tileid) => {
            //             const tile = await window.fetch(arches.urls.api_tiles(tileid), {
            //                 method: 'DELETE',
            //                 credentials: 'include',
            //                 body: JSON.stringify({'tileid': tileid})
            //             });
               
            //             if (tile.ok) {
            //                 json = await tile.json();
            //                 console.log(json);
            //             }
            //         });
            //     }
            // }
            // The above would need this corresponding fix in api.py
            // def delete(self, request, tileid):
            //     tileview = TileView()
            //     return tileview.delete(request)

            this.saveDatasetFiles = async (part, datasetNameTileResourceId) => {
                //Tile structure for the Digital Resource 'File' nodegroup
                self.savingFile(true);
                const fileTemplate = {
                    "tileid": "",
                    "data": {
                        "29d5ecb8-79a5-11ea-8ae2-acde48001122": null,
                        "7c486328-d380-11e9-b88e-a4d18cec433a": null,
                        "5e1791d4-79a5-11ea-8ae2-acde48001122": null,
                        "21d0ba4e-78eb-11ea-a33b-acde48001122": null
                    },
                    "nodegroup_id": "7c486328-d380-11e9-b88e-a4d18cec433a",
                    "parenttile_id": null,
                    "resourceinstance_id": "",
                    "sortorder": 1,
                    "tiles": {},
                    "transaction_id": params.form.workflowId
                };

                const datasetFilesArray = part.datasetFiles();
                for(let i = 0; i < datasetFilesArray.length; ++i){
                    const file = datasetFilesArray[i];
                    self.savingMessage(`Uploading ${file.name}`);
                    let fileInfo;
                    // file has already been uploaded
                    if (file.tileId()){ continue; }
                    // eslint-disable-next-line camelcase
                    fileTemplate.resourceinstance_id = datasetNameTileResourceId;
                    
                    if (!ko.unwrap(file.tileId)) {
                        fileInfo = {
                            name: file.name,
                            accepted: file.accepted,
                            height: file.height,
                            lastModified: file.lastModified,
                            size: file.size,
                            status: file.status,
                            type: file.type,
                            width: file.width,
                            url: null,
                            // eslint-disable-next-line camelcase
                            file_id: null,
                            index: i,
                            content: window.URL.createObjectURL(file),
                            error: file.error
                        };
                        if (['txt', 'dx'].includes(file.name.split('.').pop())) {
                            fileInfo.renderer = rendererLookup[observationInfo.instrument.value].rendererid;
                        } else if (file.type.split('/').includes('image')) {
                            fileInfo.renderer = rendererLookup["image"].rendererid
                        } else if (file.type.split('/').includes('pdf')) {
                            fileInfo.renderer = rendererLookup["pdf"].rendererid
                        };

                        fileTemplate.data["7c486328-d380-11e9-b88e-a4d18cec433a"] = [fileInfo];
                        const formData = new window.FormData();
                        formData.append('transaction_id', params.form.workflowId);
                        formData.append('data', JSON.stringify(fileTemplate));
                        formData.append('file-list_7c486328-d380-11e9-b88e-a4d18cec433a', file, file.name);
                        const tileId = file.tileId() || uuid.generate();
                        const tile = await window.fetch(arches.urls.api_tiles(tileId), {
                            method: 'POST',
                            credentials: 'include',
                            body: formData
                        })

                        if (tile.ok) {
                            json = await tile.json();
                            file.tileId(json.tileid);
                        }
                    }
                }
                self.savingFile(false);
            };

            this.saveDigitalResourceToChildPhysThing = async (part) => {
                const resourceReferenceId = part.resourceReferenceId()
                const filesAlreadyUploaded = part.datasetFiles().some(f => f.file_id)
                if ( resourceReferenceId || !resourceReferenceId && filesAlreadyUploaded) { 
                    return resourceReferenceId; 
                }
                const partResourceInstanceId = part.data[physicalThingPartNodeId][0].resourceId; 
                const digitalReferenceNodeId = "a298ee52-8d59-11eb-a9c4-faffc265b501";
                const digitalReferenceNodeGroupId = "8a4ad932-8d59-11eb-a9c4-faffc265b501";  
                const tileid = uuid.generate();
                const payload = [{
                    "resourceId": part.datasetId(),
                    "ontologyProperty": "",
                    "inverseOntologyProperty": ""
                }];
                const digitalReferenceTile = {
                    "tileid": "",
                    "data": {},
                    "nodegroup_id": digitalReferenceNodeGroupId,
                    "parenttile_id": null,
                    "resourceinstance_id": partResourceInstanceId,
                    "sortorder": 1,
                    "tiles": {},
                    "transaction_id": params.form.workflowId
                };
                digitalReferenceTile.data[digitalReferenceNodeId] = payload;
                const result = await window.fetch(arches.urls.api_tiles(tileid), {
                    method: 'POST',
                    credentials: 'include',
                    body: JSON.stringify(digitalReferenceTile),
                    headers: {
                        'Content-Type': 'application/json'
                    },
                });

                if(result.ok){
                    const json = await result.json();
                    part.resourceReferenceId(json?.tileid);
                    return part.resourceReferenceId();
                }
            };

            this.cancel = () => {
                if(self.canBeSaved()){
                    self.init();
                }
                self.parts.valueHasMutated();
            }

            this.save = async() => {

                params.form.lockExternalStep("select-instrument-and-files", true);
                const parts = self.parts();
                for (const part of parts) {
                    if (!part.datasetName() && part.datasetFiles().length === 0) { continue; }
                    try {
                        // For each part of parent phys thing, create a digital resource with a Name tile
                        const dataset = (await self.saveDatasetName(part));

                        part.datasetId(dataset.resourceId);
                        part.nameTileId(dataset.tileId);

                        // Then save a file tile to the digital resource for each associated file
                        await self.saveDatasetFiles(part, dataset.resourceId);
                        // await self.removeDatasetFiles(part);
                    
                        // Then save a relationship tile on the part that points to the digital resource
                        await self.saveDigitalResourceToChildPhysThing(part);
                    } catch(err) {
                        // eslint-disable-next-line no-console
                        console.log('Tile update failed', err);
                        params.form.loading(false);
                    }
                }

                try {
                    await self.createObservationCrossReferences();
                } catch(err) {
                    console.log('Couldn\'t create observation cross references.');
                }

                params.form.savedData({ 
                    observationReferenceTileId: self.observationReferenceTileId(),
                    parts: self.parts().map(x => 
                        {
                            return {
                                datasetFiles: x.datasetFiles().map(x => { return {...x, tileId: x.tileId()} }),
                                datasetId: x.datasetId(),
                                nameTileId: x.nameTileId(),
                                datasetName: x.datasetName() || '',
                                resourceReferenceId: x.resourceReferenceId(),
                                tileid: x.tileid
                            };
                        }
                    )
                });

                self.snapshot = params.form.savedData();
                params.form.complete(true);
            };

            this.dropzoneOptions = {
                url: "arches.urls.root",
                dictDefaultMessage: '',
                autoProcessQueue: false,
                uploadMultiple: true,
                autoQueue: false,
                clickable: ".upload-dataset-files." + this.uniqueidClass(),
                previewsContainer: '#hidden-dz-previews',
                init: function() {
                    self.dropzone = this;
                    this.on("addedfiles", self.addFiles);
                    this.on("error", function(file, error) {
                        file.error = error;
                    });    
                }
            };

            this.canBeSaved = ko.pureComputed(() => {
                return self.parts().filter(part => part.datasetName && !part.datasetId())
                    .some(part => part.datasetFiles().length) ||
                    self.parts().filter(part => ko.unwrap(part.datasetId)).some(part => part.datasetFiles().some(file => !file.tileId())) ||
                    self.parts().some(part => part.nameDirty());
            });

            this.init = async() => {
                this.selectedAnnotationTile.subscribe(this.highlightAnnotation);
                self.annotationNodes.subscribe(function(val){
                    var overlay = val.find(n => n.name.includes('Physical Thing'));
                    if (overlay) {
                        overlay.active(true);
                        if (ko.unwrap(overlay.annotations) && overlay.annotations().length > 0) {
                            self.highlightAnnotation();
                        }
                        overlay.annotations.subscribe(function(){
                            self.highlightAnnotation();
                        });
                    }
                });

                const thingResource = await resourceUtils.lookupResourceInstanceData(this.physicalThing);
                const parts = thingResource?._source.tiles.filter((tile) => tile.nodegroup_id === physicalThingPartNodeGroupId);

                self.observationReferenceTileId(params.form.savedData()?.observationReferenceTileId);               
                for (const part of parts) {
                    part.resourceid = part.data[physicalThingPartNodeId][0].resourceId; 
                    const related = await resourceUtils.lookupResourceInstanceData(part.resourceid);
                    const digitalReferenceNodeGroupId = "8a4ad932-8d59-11eb-a9c4-faffc265b501"; 
                    const digitalReferenceNodeId = "a298ee52-8d59-11eb-a9c4-faffc265b501";
                    const digitalReferenceTypeNodeId = 'f11e4d60-8d59-11eb-a9c4-faffc265b501';
                    const datasetTile = related?._source.tiles.find((tile) => tile.nodegroup_id === digitalReferenceNodeGroupId);
                    const manifestValueIds = [
                        '1497d15a-1c3b-4ee9-a259-846bbab012ed', // Preferred Manifest
                        '305c62f0-7e3d-4d52-a210-b451491e6100', // IIIF Manifest
                        '00d5a7a6-ff2f-4c44-ac85-7a8ab1a6fb70' // Alternate Manifest
                    ];
                    const datasetValueIds = [
                        '4bb83364-a32a-493a-b3c9-b0aa6f279d51', // Dataset
                        'fe03bc60-ba4e-4fd0-97db-66af93bcc703', // FORS Dataset
                        'c7812e3b-7576-4b78-a033-f82c6f96e6d2', // Raman dataset
                        'bf173b8f-c883-468b-bf08-dea52f5864ff', // XRF Dataset
				'baf93c49-d215-4fcb-a422-dc1d629664ee', // UV-Vis Dataset
                    ];
                    part.datasetFiles = part.datasetFiles || ko.observableArray([]);
                    part.datasetName = part.datasetName || ko.observable();

                    const childPhysThingName = related._source.displayname;
                    part.calcDatasetName = ko.computed(function() {
                        const basename = part.datasetName() || 'Dataset';
                        return `${basename} (${childPhysThingName})`
                    });
    
                    part.datasetId = part.datasetId || ko.observable();
                    part.nameTileId = part.nameTileId || ko.observable();
                    part.resourceReferenceId = part.resourceReferenceId || ko.observable();
                    part.nameDirty = part.nameDirty || ko.observable(false);
                    part.displayname = part.data[physicalThingPartNameNodeId];
                    if (datasetTile && !manifestValueIds.includes(datasetTile.data[digitalReferenceTypeNodeId])) {
                        const dataset = await resourceUtils.lookupResourceInstanceData(datasetTile.data[digitalReferenceNodeId][0].resourceId);
                        const datasetName =  dataset._source.tiles.find((tile) => tile.nodegroup_id === datasetNameNodeGroupId).data[datasetNameNodeId];
                        const nameTileId =  dataset._source.tiles.find((tile) => tile.nodegroup_id === datasetNameNodeGroupId).tileid;
                        const datasetTiles =  dataset._source.tiles.filter((tile) => tile.nodegroup_id === datasetFileNodeGroupId)
                        const datasetFiles = datasetTiles.map((tile) => {
                            let file = tile.data[datasetFileNodeId][0];
                            file.tileId = ko.observable(tile.tileid);
                            return file;
                        });
                        part.datasetId(dataset._id);
                        part.datasetName(datasetName);
                        part.datasetFiles(datasetFiles);
                        part.nameTileId(nameTileId);
                    }
                    
                    if(!part.datasetId.getSubscriptionsCount()){
                        part.datasetId.subscribe(function(val){
                            if (val) {
                                params.form.complete(true);
                            }
                        });
                    }
                    const savedValue = params.form.savedData()?.parts?.filter(x => x.tileid == part.tileid)?.[0];
                    if(savedValue) {
                        
                        part.datasetFiles(savedValue.datasetFiles.map(x => { return {...x, tileId:ko.observable(x.tileId)}}));
                        part.datasetName(savedValue.datasetName);
                        part.datasetId(savedValue.datasetId);
                        part.nameTileId(savedValue.nameTileId);
                        part.resourceReferenceId(savedValue.resourceReferenceId);
                        if(self.activeTab() != 'dataset') {
                            self.mainMenu(false);
                            self.activeTab('dataset');
                            self.annotationNodes.valueHasMutated();
                        }
                    }
                    if(part.datasetName.getSubscriptionsCount()){
                        part.datasetName.subscribe((newValue) => {
                            const datasetSnapshot = self.snapshot?.parts?.find(x => x.datasetId == part.datasetId());
                            if(newValue != datasetSnapshot?.datasetName) {
                                part.nameDirty(true);
                            } else {
                                part.nameDirty(false);
                            }
                        });
                    }
                };
                self.parts(parts);
                self.save();
                self.selectedPart(self.parts()[0]);
            }
     
            this.init();
        },
        template: { require: 'text!templates/views/components/workflows/upload-dataset/select-dataset-files-step.htm' }
    });
});