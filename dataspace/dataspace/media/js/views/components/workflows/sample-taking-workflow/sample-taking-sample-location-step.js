define([
    'underscore',
    'jquery',
    'arches',
    'views/components/workflows/stepUtils',
    'knockout',
    'knockout-mapping',
    'utils/resource',
    'models/graph',
    'viewmodels/card',
    'views/components/iiif-annotation',
    'text!templates/views/components/iiif-popup.htm',
], function(_, $, arches, StepUtils, ko, koMapping, ResourceUtils, GraphModel, CardViewModel, IIIFAnnotationViewmodel, iiifPopup) {
    function viewModel(params) {
        var self = this;
        _.extend(this, params);

        this.physicalThingResourceId = koMapping.toJS(params.physicalThingResourceId);
        this.samplingActivityResourceId = koMapping.toJS(params.samplingActivityResourceId);
        
        var digitalResourceServiceIdentifierContentNodeId = '56f8e9bd-ca7c-11e9-b578-a4d18cec433a';
        const partIdentifierAssignmentPhysicalPartOfObjectNodeId = 'b240c366-8594-11ea-97eb-acde48001122';
        const samplingUnitNodegroupId = 'b3e171a7-1d9d-11eb-a29f-024e0d439fdb';
        const sampleMotivationConceptId = "7060892c-4d91-4ab3-b3de-a95e19931a61";
        const samplingActivityGraphId = "03357848-1d9d-11eb-a29f-024e0d439fdb";
        const physicalThingPartAnnotationNodeId = "97c30c42-8594-11ea-97eb-acde48001122";
        this.analysisAreaResourceIds = [];
        this.manifestUrl = ko.observable(params.imageServiceInstanceData[digitalResourceServiceIdentifierContentNodeId]);

        this.samplingActivitySamplingUnitCard = ko.observable();
        this.samplingActivityStatementCard = ko.observable();
        this.physThingSearchResultsLookup = {};
        this.savingTile = ko.observable();
        this.savingMessage = ko.observable();

        this.selectedFeature = ko.observable();
        this.featureLayers = ko.observableArray();
        this.isFeatureBeingEdited = ko.observable(false);

        this.physicalThingPartIdentifierAssignmentCard = ko.observable();
        this.physicalThingPartIdentifierAssignmentTile = ko.observable();

        this.partIdentifierAssignmentLabelWidget = ko.observable();
        this.partIdentifierAssignmentPolygonIdentifierWidget = ko.observable();

        this.previouslySavedSampleDescriptionWidgetValue = ko.observable();
        this.sampleDescriptionWidgetValue = ko.observable();

        this.previouslySavedMotivationForSamplingWidgetValue = ko.observable();
        this.motivationForSamplingWidgetValue = ko.observable();

        this.activeTab = ko.observable();
        this.hasExternalCardData = ko.observable(false);

        this.sampleLocationInstances = ko.observableArray();
        
        this.selectedSampleLocationInstance = ko.observable();
        this.selectedSampleRelatedSamplingActivity = ko.observable();

        this.sampleLocationDisabled = ko.computed(() => {
            if(self.samplingActivityResourceId != self.selectedSampleRelatedSamplingActivity()){
                return true;
            } else {
                return false;
            }
        })

        this.switchCanvas = function(tile){
            const features = ko.unwrap(tile.data[physicalThingPartAnnotationNodeId].features)
            const canvasPath = features?.[0]?.properties.canvas()
            if (self.canvas() !== canvasPath) {
                var canvas = self.canvases().find(c => c.images[0].resource.service['@id'] === canvasPath);
                if (canvas) {
                    self.canvasClick(canvas);       
                }
            }
        };

        this.selectedSampleLocationInstance.subscribe(function(selectedSampleLocationInstance) {
            self.highlightAnnotation();

            if (selectedSampleLocationInstance) {
                self.tile = selectedSampleLocationInstance;
                params.tile = selectedSampleLocationInstance;
                self.physicalThingPartIdentifierAssignmentTile(selectedSampleLocationInstance);
                if (ko.unwrap(ko.unwrap(selectedSampleLocationInstance.data[physicalThingPartAnnotationNodeId])?.features)) {
                    self.switchCanvas(selectedSampleLocationInstance)
                }
            }
        });

        this.tileDirty = ko.computed(function() {
            if(self.sampleLocationDisabled()){
                return false;
            }
            if (
                self.sampleDescriptionWidgetValue() && self.sampleDescriptionWidgetValue() !== self.previouslySavedSampleDescriptionWidgetValue()
            ) {
                return true;
            }
            else if (
                self.motivationForSamplingWidgetValue() && self.motivationForSamplingWidgetValue() !== self.previouslySavedMotivationForSamplingWidgetValue()
            ) {
                return true;
            }
            else if (self.physicalThingPartIdentifierAssignmentTile()) {
                return self.physicalThingPartIdentifierAssignmentTile().dirty();
            }
        });

        this.selectedSampleLocationInstanceFeatures = ko.computed(function() {
            var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)

            if (self.selectedSampleLocationInstance()) {
                if (ko.unwrap(self.selectedSampleLocationInstance().data[partIdentifierAssignmentPolygonIdentifierNodeId])) {
                    var partIdentifierAssignmentPolygonIdentifierData = ko.unwrap(self.selectedSampleLocationInstance().data[partIdentifierAssignmentPolygonIdentifierNodeId]);
                    return ko.unwrap(partIdentifierAssignmentPolygonIdentifierData.features);
                }
            }
        });

        this.sampleLocationFilterTerm = ko.observable();
        this.filteredSampleLocationInstances = ko.computed(function() {
            const samplesOnly = self.sampleLocationInstances().filter(function(a){
                const analysisAreaResourceIds = self.analysisAreaResourceIds.map(item => item.resourceid);
                const partId = ko.unwrap(a.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId]()[0].resourceId)
                return !analysisAreaResourceIds.includes(partId);
            });
            if (self.sampleLocationFilterTerm()) {
                return samplesOnly.filter(function(sampleLocationInstance) {
                    var partIdentifierAssignmentLabelNodeId = '3e541cc6-859b-11ea-97eb-acde48001122';
                    return sampleLocationInstance.data[partIdentifierAssignmentLabelNodeId]().includes(self.sampleLocationFilterTerm());
                });
            }
            else {
                return samplesOnly;
            }
        });

        this.hasExternalCardData.subscribe(function(hasExternalCardData) {
            if (hasExternalCardData) {
                self.handleExternalCardData();

                var physicalThingGeometriestAnnotationSubscription = self.annotationNodes.subscribe(function(annotationNodes) {
                    self.setPhysicalThingGeometriesToVisible(annotationNodes);
                    physicalThingGeometriestAnnotationSubscription.dispose(); /* self-disposing subscription only runs once */
                });

                self.activeTab('dataset');

                self.manifest(self.manifestUrl());
                self.getManifestData();
            }
        });

        this.sampleName = ko.computed(function() {
            var partIdentifierAssignmentLabelNodeId = '3e541cc6-859b-11ea-97eb-acde48001122';
            if (self.selectedSampleLocationInstance()){
                const baseName = self.selectedSampleLocationInstance().data[partIdentifierAssignmentLabelNodeId]() || "";
                return `${baseName} [Sample of ${params.physicalThingName}]`;
            }
        })

        this.initialize = function() {
            params.form.save = self.saveWorkflowStep;

            $.getJSON(arches.urls.api_card + self.physicalThingResourceId).then(function(data) {
                self.loadExternalCardData(data);
            });

            self.fetchCardFromResourceId(self.samplingActivityResourceId, samplingUnitNodegroupId).then(function(samplingActivitySamplingUnitCard) {
                self.samplingActivitySamplingUnitCard(samplingActivitySamplingUnitCard);
            });

            // var samplingActivityStatementNodegroupId = '0335786d-1d9d-11eb-a29f-024e0d439fdb';  // Statement (E33)

            // self.fetchCardFromResourceId(self.samplingActivityResourceId, samplingActivityStatementNodegroupId).then(function(samplingActivityStatementCard) {
            //     self.samplingActivityStatementCard(samplingActivityStatementCard);
            // });
        };

        this.getSampleLocationTileFromFeatureId = function(featureId) {
            var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)

            return self.sampleLocationInstances().find(function(sampleLocationInstance) {
                var sampleLocationInstanceFeatures = sampleLocationInstance.data[partIdentifierAssignmentPolygonIdentifierNodeId].features();

                return sampleLocationInstanceFeatures.find(function(sampleLocationInstanceFeature) {
                    return ko.unwrap(sampleLocationInstanceFeature.id) === featureId;
                });
            });
        };

        this.getAnnotationProperty = function(tile, property){
            return tile.data[self.annotationNodeId].features[0].properties[property];
        };

        this.highlightAnnotation = function(){
            if (self.map()) {
                self.map().eachLayer(function(layer){
                    if (layer.eachLayer) {
                        layer.eachLayer(function(features){
                            if (features.eachLayer) {
                                features.eachLayer(function(feature) {
                                    var defaultColor = feature.feature.properties.color;
                                    
                                    if (self.selectedSampleLocationInstance() && self.selectedSampleLocationInstance().tileid === feature.feature.properties.tileId) {
                                        feature.setStyle({color: '#BCFE2B', fillColor: '#BCFE2B'});
                                    } else {
                                        feature.setStyle({color: defaultColor, fillColor: defaultColor});
                                    }
                                });
                            }
                        });
                    }
                })
            } 
        };

        this.removeFeatureFromCanvas = function(feature) {
            var annotationNodes = self.annotationNodes();
            
            var physicalThingAnnotationNodeName = "Sample Locations";
            var physicalThingAnnotationNode = annotationNodes.find(function(annotationNode) {
                return annotationNode.name === physicalThingAnnotationNodeName;
            });

            var filteredPhysicalThingAnnotationNodeAnnotations = physicalThingAnnotationNode.annotations().filter(function(annotation) {
                return ko.unwrap(feature.id) !== annotation.id;
            });

            physicalThingAnnotationNode.annotations(filteredPhysicalThingAnnotationNodeAnnotations);

            var physicalThingAnnotationNodeIndex = annotationNodes.findIndex(function(annotationNode) {
                return annotationNode.name === physicalThingAnnotationNodeName;
            });

            annotationNodes[physicalThingAnnotationNodeIndex] = physicalThingAnnotationNode;

            self.annotationNodes(annotationNodes);

            self.highlightAnnotation();
        }

        this.resetCanvasFeatures = function() {
            var annotationNodes = self.annotationNodes();
            
            if (self.selectedSampleLocationInstanceFeatures()) {
                var physicalThingAnnotationNodeName = "Sample Locations";
                var physicalThingAnnotationNode = annotationNodes.find(function(annotationNode) {
                    return annotationNode.name === physicalThingAnnotationNodeName;
                });
    
                var physicalThingAnnotationNodeAnnotationIds = physicalThingAnnotationNode.annotations().map(function(annotation) {
                    return ko.unwrap(annotation.id);
                });
                
                var unaddedSelectedSampleLocationInstanceFeatures = self.selectedSampleLocationInstanceFeatures().reduce(function(acc, feature) {
                    if (!physicalThingAnnotationNodeAnnotationIds.includes(ko.unwrap(feature.id)) &&
                        feature.properties.canvas === self.canvas) {
                        feature.properties.tileId = self.selectedSampleLocationInstance().tileid;
                        acc.push(ko.toJS(feature));
                    }
    
                    return acc;
                }, []);
    
                physicalThingAnnotationNode.annotations([...physicalThingAnnotationNode.annotations(), ...unaddedSelectedSampleLocationInstanceFeatures]);
    
                var physicalThingAnnotationNodeIndex = annotationNodes.findIndex(function(annotationNode) {
                    return annotationNode.name === physicalThingAnnotationNodeName;
                });
    
                annotationNodes[physicalThingAnnotationNodeIndex] = physicalThingAnnotationNode;
            }

            self.annotationNodes(annotationNodes);
        };

        this.updateSampleLocationInstances = function() {
            canvasids = self.canvases().map(canvas => canvas.images[0].resource['@id'])
            const tilesBelongingToManifest = self.card.tiles().filter(
                tile => canvasids.find(
                    canvas => canvas.startsWith(tile.data[physicalThingPartAnnotationNodeId].features()[0].properties.canvas())
                    )
                );

            tilesBelongingToManifest.forEach(tile => tile.samplingActivityResourceId = tile.samplingActivityResourceId ? tile.samplingActivityResourceId : ko.observable());
            self.sampleLocationInstances(tilesBelongingToManifest);
        };

        this.sampleLocationInstances.subscribe(async (instances) => {
            for(const instance of instances) {
                const instanceResourceId = ko.unwrap(ko.unwrap(instance.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId])?.[0]?.resourceId);
                const currentResourceRelatedResources = await(await window.fetch(`${arches.urls.related_resources}${instanceResourceId}`)).json();
                const relatedSamplingActivity = currentResourceRelatedResources?.related_resources?.related_resources?.filter(x => x?.graph_id == samplingActivityGraphId);
                instance.samplingActivityResourceId(relatedSamplingActivity?.[0]?.resourceinstanceid);
            }
        });

        this.selectSampleLocationInstance = async function(sampleLocationInstance) {
            self.sampleDescriptionWidgetValue(null);
            self.previouslySavedSampleDescriptionWidgetValue(null);
            
            self.motivationForSamplingWidgetValue(null);
            self.previouslySavedMotivationForSamplingWidgetValue(null);

            var previouslySelectedSampleLocationInstance = self.selectedSampleLocationInstance();

            /* resets any changes not explicity saved to the tile */ 
            if (previouslySelectedSampleLocationInstance && previouslySelectedSampleLocationInstance.tileid !== sampleLocationInstance.tileid) {
                previouslySelectedSampleLocationInstance.reset();

                self.drawFeatures([]);
                self.resetCanvasFeatures();
            }

            if (self.physicalThingPartIdentifierAssignmentTile()) {
                self.physicalThingPartIdentifierAssignmentTile().reset();
            }

            self.selectedSampleLocationInstance(sampleLocationInstance);

            if (self.selectedSampleLocationInstance()) {

                var selectedSampleLocationParentPhysicalThingData = ko.unwrap(self.selectedSampleLocationInstance().data[partIdentifierAssignmentPhysicalPartOfObjectNodeId]);
                
                var selectedSampleLocationParentPhysicalThingResourceId;
                if (selectedSampleLocationParentPhysicalThingData) {
                    selectedSampleLocationParentPhysicalThingResourceId = ko.unwrap(selectedSampleLocationParentPhysicalThingData[0].resourceId);
                } 

                let samplingActivitySamplingUnitCard = self.samplingActivitySamplingUnitCard();
                if(self.selectedSampleLocationInstance()?.samplingActivityResourceId) {
                    self.selectedSampleRelatedSamplingActivity(self.selectedSampleLocationInstance().samplingActivityResourceId());
                } else if (selectedSampleLocationParentPhysicalThingResourceId){
                    const selectedResourceRelatedResources = await(await window.fetch(`${arches.urls.related_resources}${selectedSampleLocationParentPhysicalThingResourceId}`)).json();
                    const relatedSamplingActivity = selectedResourceRelatedResources?.related_resources?.related_resources?.filter(x => x?.graph_id == samplingActivityGraphId);
                    self.selectedSampleRelatedSamplingActivity(relatedSamplingActivity?.[0].resourceinstanceid);
                } else {
                    self.selectedSampleRelatedSamplingActivity(self.samplingActivityResourceId);
                }

                if(self.selectedSampleRelatedSamplingActivity() && self.selectedSampleRelatedSamplingActivity() != self.samplingActivityResourceId) {
                    samplingActivitySamplingUnitCard = await self.fetchCardFromResourceId(self.selectedSampleRelatedSamplingActivity(), samplingUnitNodegroupId);
                }

                if(!samplingActivitySamplingUnitCard) { return; }

                var samplingAreaNodeId = 'b3e171ac-1d9d-11eb-a29f-024e0d439fdb';  // Sampling Area (E22)
                var samplingActivitySamplingUnitTile = samplingActivitySamplingUnitCard.tiles().find(function(tile) {
                    var data = ko.unwrap(tile.data[samplingAreaNodeId]);

                    if (data) {
                        return ko.unwrap(data[0].resourceId) === selectedSampleLocationParentPhysicalThingResourceId;
                    }
                });

                if (samplingActivitySamplingUnitTile) {
                    var samplingAreaSampleCreatedNodeId = 'b3e171ab-1d9d-11eb-a29f-024e0d439fdb';  // Sample Created (E22)
                    var samplingAreaSampleCreatedParentPhysicalThingResourceId = ko.unwrap(samplingActivitySamplingUnitTile.data[samplingAreaSampleCreatedNodeId])[0].resourceId();
                    
                    var physicalThingStatementNodegroupId = '1952bb0a-b498-11e9-a679-a4d18cec433a';  // Statement (E33)
    
                    self.fetchCardFromResourceId(samplingAreaSampleCreatedParentPhysicalThingResourceId, physicalThingStatementNodegroupId).then(function(samplingAreaSampleCreatedParentPhysicalThingStatementCard) {
                        var physicalThingStatementTypeNodeId = '1952e470-b498-11e9-b261-a4d18cec433a'; // Statement_type (E55)
                        var physicalThingStatementContentNodeId = '1953016e-b498-11e9-9445-a4d18cec433a';  // Statement_content (xsd:string)

                        var sampleDescriptionConceptId = "9886efe9-c323-49d5-8d32-5c2a214e5630";

                        var sampleDescriptionTile = samplingAreaSampleCreatedParentPhysicalThingStatementCard.tiles().find(function(tile) {
                            return ko.unwrap(tile.data[physicalThingStatementTypeNodeId]).includes(sampleDescriptionConceptId);
                        });
        
                        var samplingMotivationTile = samplingAreaSampleCreatedParentPhysicalThingStatementCard.tiles().find(function(tile) {
                            return ko.unwrap(tile.data[physicalThingStatementTypeNodeId]).includes(sampleMotivationConceptId);
                        });

                        if (sampleDescriptionTile) {
                            var sampleDescriptionContent = ko.unwrap(sampleDescriptionTile.data[physicalThingStatementContentNodeId]);

                            self.sampleDescriptionWidgetValue(sampleDescriptionContent);
                            self.previouslySavedSampleDescriptionWidgetValue(sampleDescriptionContent);
                        }

                        if (samplingMotivationTile) {
                            var sampleMotivationContent = ko.unwrap(samplingMotivationTile.data[physicalThingStatementContentNodeId]);
            
                            self.motivationForSamplingWidgetValue(sampleMotivationContent);
                            self.previouslySavedMotivationForSamplingWidgetValue(sampleMotivationContent);
                        }
                    });
                }
            }
        };

        this.resetDescriptions = function(){
            const previouslySavedSampleDescriptionWidgetValue = ko.unwrap(self.previouslySavedSampleDescriptionWidgetValue);
            const previouslySavedMotivationForSamplingWidgetValue = ko.unwrap(self.previouslySavedMotivationForSamplingWidgetValue);
            
            self.sampleDescriptionWidgetValue(previouslySavedSampleDescriptionWidgetValue);
            self.motivationForSamplingWidgetValue(previouslySavedMotivationForSamplingWidgetValue);

        }

        this.resetSampleLocationTile = function() {
            self.tile.reset();
            self.resetCanvasFeatures();
            self.resetDescriptions();
            self.drawFeatures([]);
            self.highlightAnnotation();
            self.selectedFeature(null);
        };

        this.setPhysicalThingGeometriesToVisible = function(annotationNodes) {
            var physicalThingAnnotationNodeName = "Sample Locations";
            var physicalThingAnnotationNode = annotationNodes.find(function(annotationNode) {
                return annotationNode.name === physicalThingAnnotationNodeName;
            });

            physicalThingAnnotationNode.active(true); 
            self.updateSampleLocationInstances();
        };

        this.saveSampleLocationTile = function() {
            // don't save if tile isn't dirty.
            if(!self.tileDirty()){ return; }

            var partIdentifierAssignmentLabelNodeId = '3e541cc6-859b-11ea-97eb-acde48001122';
            var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122"
            const featureCollection = ko.unwrap(self.selectedSampleLocationInstance().data[partIdentifierAssignmentPolygonIdentifierNodeId])
            if (!ko.unwrap(featureCollection?.features)?.length ||
                !self.selectedSampleLocationInstance().data[partIdentifierAssignmentLabelNodeId]()) { //Sample Name Node
                    params.pageVm.alert(new params.form.AlertViewModel(
                        "ep-alert-red",
                        "Missing Values",
                        "Sample Location and Sample Name are Required",
                    ));
                    return;    
                }

            var savePhysicalThingNameTile = function(physicalThingNameTile, type) {
                return new Promise(function(resolve, _reject) {
                    var selectedSampleLocationInstanceLabel = ko.unwrap(self.sampleName);
                    var physicalThingNameContentNodeId = 'b9c1d8a6-b497-11e9-876b-a4d18cec433a'; // Name_content (xsd:string)

                    if (type === "region") {
                        const baseName = self.selectedSampleLocationInstance().data[partIdentifierAssignmentLabelNodeId]() || "";
                        selectedSampleLocationInstanceLabel = `${baseName} [Sample Area of ${params.physicalThingName}]`;
                    }
                    
                    physicalThingNameTile.data[physicalThingNameContentNodeId] = selectedSampleLocationInstanceLabel;
                    physicalThingNameTile.transactionId = params.form.workflowId;

                    physicalThingNameTile.save().then(function(physicalThingNameData) {
                        resolve(physicalThingNameData);
                    });
                });
            };

            const savePhysicalThingClassificationTile = function(physicalThingClassificationTile, type) {
                const sampleLocationTypeConceptId = '7375a6fb-0bfb-4bcf-81a3-6180cdd26123';
                const sampleTypeConceptId = '77d8cf19-ce9c-4e0a-bde1-9148d870e11c';
                return new Promise(function(resolve, _reject) {
                    const physicalThingClassificationNodeId = '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a'; // type (E55)
                    if (type === "region") {
                        physicalThingClassificationTile.data[physicalThingClassificationNodeId] = [sampleLocationTypeConceptId];
                    }
                    else { // type === "sample"
                        physicalThingClassificationTile.data[physicalThingClassificationNodeId] = [sampleTypeConceptId];
                    }
                    physicalThingClassificationTile.transactionId = params.form.workflowId;

                    physicalThingClassificationTile.save().then(function(physicalThingClassificationData) {
                        resolve(physicalThingClassificationData);
                    });
                });
            };

            var savePhysicalThingPartOfTile = function(physicalThingPartOfTile) {
                var physicalThingPartOfNodeId = 'f8d5fe4c-b31d-11e9-9625-a4d18cec433a'; // part of (E22)

                return new Promise(function(resolve, _reject) {
                    physicalThingPartOfTile.data[physicalThingPartOfNodeId] = [{
                        "resourceId": self.physicalThingResourceId,
                        "ontologyProperty": "",
                        "inverseOntologyProperty": ""
                    }];
                    physicalThingPartOfTile.transactionId = params.form.workflowId;

                    physicalThingPartOfTile.save().then(function(physicalThingPartOfData) {
                        resolve(physicalThingPartOfData);
                    });
                });
            };

            var saveSelectedSampleLocationInstance = function(physicalThingPartOfData) {
                return new Promise(function(resolve, _reject) {
                    /* assigns Physical Thing to be the Part Identifier on the parent selected Physical Thing  */ 
                    var physicalThingPartOfNodeId = 'f8d5fe4c-b31d-11e9-9625-a4d18cec433a'; // part of (E22)
                    var physicalThingPartOfResourceXResourceId = physicalThingPartOfData.data[physicalThingPartOfNodeId][0]['resourceXresourceId'];
                    
                    var selectedSampleLocationInstance = self.selectedSampleLocationInstance();
    
                    selectedSampleLocationInstance.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId]([{
                        "resourceId": physicalThingPartOfData.resourceinstance_id,
                        "resourceXresourceId": physicalThingPartOfResourceXResourceId,
                        "ontologyProperty": "",
                        "inverseOntologyProperty": ""
                    }]);
                    selectedSampleLocationInstance.transactionId = params.form.workflowId
    
                    selectedSampleLocationInstance.save().then(function(data) {
                        resolve(data);
                    });
                });
            };

            var updateAnnotations = function() {
                return new Promise(function(resolve, _reject) {
                    /* updates selected annotations */ 
                    var physicalThingAnnotationNodeName = "Sample Locations";
                    var physicalThingAnnotationNode = self.annotationNodes().find(function(annotationNode) {
                        return annotationNode.name === physicalThingAnnotationNodeName;
                    });
    
                    var physicalThingAnnotations = physicalThingAnnotationNode.annotations();
    
                    self.drawFeatures().forEach(function(drawFeature) {
                        var annotationFeature = physicalThingAnnotations.find(function(annotation) {
                            return annotation.id === drawFeature;
                        });
    
                        drawFeature.properties.nodegroupId = self.tile.nodegroup_id;
                        drawFeature.properties.resourceId = self.tile.resourceinstance_id;
                        drawFeature.properties.tileId = self.tile.tileid;
    
                        if (!annotationFeature) {
                            physicalThingAnnotations.push(drawFeature);
                        }
                    });
    
                    physicalThingAnnotationNode.annotations(physicalThingAnnotations);

                    resolve(physicalThingAnnotationNode)
                });
            };

            var getWorkingTile = function(card) {
                /* 
                    If an auto-generated resource has a tile with data, this will return it.
                    Otherwise it returns a new tile for the card.
                */ 

                var tile = null;
                
                /* Since this is an autogenerated resource, we can assume only one associated tile. */ 
                if (card.tiles() && card.tiles().length) {
                    tile = card.tiles()[0];
                }
                else {
                    tile = card.getNewTile();
                }

                return tile;
            };

            var getWorkingSamplingActivityUnitTile = function(samplingActivitySamplingUnitCard, regionPhysicalThingNameData) {
                var samplingAreaNodeId = 'b3e171ac-1d9d-11eb-a29f-024e0d439fdb';  // Sampling Area (E22)

                var samplingActivitySamplingUnitTile;
                if (samplingActivitySamplingUnitCard.tiles() && samplingActivitySamplingUnitCard.tiles().length) {
                    var previouslySavedTile = samplingActivitySamplingUnitCard.tiles().find(function(tile) {
                        var data = ko.unwrap(tile.data[samplingAreaNodeId]);

                        if (data) {
                            return ko.unwrap(data[0].resourceId) === regionPhysicalThingNameData.resourceinstance_id;
                        }
                    });

                    if (previouslySavedTile) {
                        samplingActivitySamplingUnitTile = previouslySavedTile;
                    }
                    else {
                        samplingActivitySamplingUnitTile = samplingActivitySamplingUnitCard.getNewTile();
                    }
                }
                else {
                    samplingActivitySamplingUnitTile = samplingActivitySamplingUnitCard.getNewTile();
                }

                return samplingActivitySamplingUnitTile;
            };

            var saveSamplingActivitySamplingUnitTile = function(samplingActivitySamplingUnitTile, regionPhysicalThingNameData, samplePhysicalThingNameData) {
                return new Promise(function(resolve, _reject) {
                    var samplingAreaNodeId = 'b3e171ac-1d9d-11eb-a29f-024e0d439fdb';  // Sampling Area (E22)
                    
                    samplingActivitySamplingUnitTile.data[samplingAreaNodeId] = [{
                        "resourceId": regionPhysicalThingNameData.resourceinstance_id,
                        "ontologyProperty": "",
                        "inverseOntologyProperty": ""
                    }];

                    var samplingAreaOverallObjectSampledNodeId = 'b3e171aa-1d9d-11eb-a29f-024e0d439fdb';  //  Overall Object Sampled (E22)
                    samplingActivitySamplingUnitTile.data[samplingAreaOverallObjectSampledNodeId] = [{
                        "resourceId": self.physicalThingResourceId,
                        "ontologyProperty": "",
                        "inverseOntologyProperty": ""
                    }];

                    var samplingAreaSampleCreatedNodeId = 'b3e171ab-1d9d-11eb-a29f-024e0d439fdb';  // Sample Created (E22)
                    samplingActivitySamplingUnitTile.data[samplingAreaSampleCreatedNodeId] = [{
                        "resourceId": samplePhysicalThingNameData.resourceinstance_id,
                        "ontologyProperty": "",
                        "inverseOntologyProperty": ""
                    }];

                    var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)
                    var samplingAreaVisualizationNodeId = 'b3e171ae-1d9d-11eb-a29f-024e0d439fdb';  // Sampling Area Visualization (E42)

                    samplingActivitySamplingUnitTile.data[samplingAreaVisualizationNodeId] = ko.toJS(
                        self.physicalThingPartIdentifierAssignmentTile().data[partIdentifierAssignmentPolygonIdentifierNodeId]
                    );
                    samplingActivitySamplingUnitTile.transactionId = params.form.workflowId;

                    samplingActivitySamplingUnitTile.save().then(function(data) {
                        resolve(data);
                    });
                });
            };

            var getRegionPhysicalThingNameCard = function() {
                return new Promise(function(resolve, _reject) {
                    var physicalThingNameNodegroupId = 'b9c1ced7-b497-11e9-a4da-a4d18cec433a';  // Name (E33)
                    var partIdentifierAssignmentPhysicalPartOfObjectData = ko.unwrap(self.tile.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId]);
        
                    if (partIdentifierAssignmentPhysicalPartOfObjectData) { /* if editing Physical Thing */
                        var partIdentifierAssignmentPhysicalPartOfObjectResourceId = partIdentifierAssignmentPhysicalPartOfObjectData[0]['resourceId']();
        
                        self.fetchCardFromResourceId(partIdentifierAssignmentPhysicalPartOfObjectResourceId, physicalThingNameNodegroupId).then(function(physicalThingNameCard) {
                            resolve(physicalThingNameCard);
                        });
                    }
                    else {
                        var physicalThingGraphId = '9519cb4f-b25b-11e9-8c7b-a4d18cec433a';
        
                        self.fetchCardFromGraphId(physicalThingGraphId, physicalThingNameNodegroupId).then(function(physicalThingNameCard) { 
                            resolve(physicalThingNameCard);
                        });
                    }

                });
            };

            var getSamplePhysicalThingNameCard = function(samplingActivitySamplingUnitTile) {
                return new Promise(function(resolve, _reject) {
                    var samplingUnitSampleCreatedNodeId = 'b3e171ab-1d9d-11eb-a29f-024e0d439fdb';  // Sample Created (E22)
                    var samplingUnitSampleCreatedData = ko.unwrap(samplingActivitySamplingUnitTile.data[samplingUnitSampleCreatedNodeId]);
    
                    var physicalThingNameNodegroupId = 'b9c1ced7-b497-11e9-a4da-a4d18cec433a';  // Name (E33)

                    if (samplingUnitSampleCreatedData) {
                        /* name card of physical thing representing sample */ 
                        self.fetchCardFromResourceId(samplingUnitSampleCreatedData[0].resourceId(), physicalThingNameNodegroupId).then(function(samplingUnitSampleCreatedCard) {
                            resolve(samplingUnitSampleCreatedCard);
                        });
                    }
                    else {
                        var physicalThingGraphId = '9519cb4f-b25b-11e9-8c7b-a4d18cec433a';
    
                        self.fetchCardFromGraphId(physicalThingGraphId, physicalThingNameNodegroupId).then(function(samplingUnitSampleCreatedCard) { 
                            resolve(samplingUnitSampleCreatedCard);
                        });
                    }
                });              
            };

            var getWorkingPhysicalThingSamplingDescriptionTile = function(physicalThingStatementCard) {
                var sampleDescriptionConceptId = "9886efe9-c323-49d5-8d32-5c2a214e5630"
                var physicalThingStatementTypeNodeId = "1952e470-b498-11e9-b261-a4d18cec433a"; // Statement_type (E55)

                if (physicalThingStatementCard.tiles() && physicalThingStatementCard.tiles().length) {

                    var previouslySavedTile = physicalThingStatementCard.tiles().find(function(tile) {
                        return ko.unwrap(tile.data[physicalThingStatementTypeNodeId]).includes(sampleDescriptionConceptId);
                    });

                    if (previouslySavedTile) {
                        return previouslySavedTile;
                    }
                    else {
                        return physicalThingStatementCard.getNewTile();
                    }
                }
                else {
                    return physicalThingStatementCard.getNewTile();
                }
            };

            var getWorkingPhysicalThingSamplingMotivationTile = function(physicalThingStatementCard) {
                var physicalThingStatementTypeNodeId = "1952e470-b498-11e9-b261-a4d18cec433a"; // Statement_type (E55)

                if (physicalThingStatementCard.tiles() && physicalThingStatementCard.tiles().length) {

                    var previouslySavedTile = physicalThingStatementCard.tiles().find(function(tile) {
                        return ko.unwrap(tile.data[physicalThingStatementTypeNodeId]).includes(sampleMotivationConceptId);
                    });

                    if (previouslySavedTile) {
                        return previouslySavedTile;
                    }
                    else {
                        return physicalThingStatementCard.getNewTile();
                    }
                }
                else {
                    return physicalThingStatementCard.getNewTile();
                }
            };


            var savePhysicalThingStatementTile = function(physicalThingStatementTile, type) {
                var sampleDescriptionConceptId = "9886efe9-c323-49d5-8d32-5c2a214e5630";

                return new Promise(function(resolve, _reject) {
                    if (self.sampleDescriptionWidgetValue()) {
                        var physicalThingStatementContentNodeId = '1953016e-b498-11e9-9445-a4d18cec433a';  // Statement_content (xsd:string)
                        var physicalThingStatementTypeNodeId = '1952e470-b498-11e9-b261-a4d18cec433a'; // Statement_type (E55)
    
                        var physicalThingStatementTypeData = ko.unwrap(physicalThingStatementTile.data[physicalThingStatementTypeNodeId]);

                        if (type === "description") {
                            physicalThingStatementTile.data[physicalThingStatementContentNodeId] = self.sampleDescriptionWidgetValue();
                            if (!physicalThingStatementTypeData.includes(sampleDescriptionConceptId)) {
                                physicalThingStatementTypeData = [sampleDescriptionConceptId];
                            }
                        } else if (type === "motivation") {
                            physicalThingStatementTile.data[physicalThingStatementContentNodeId] = self.motivationForSamplingWidgetValue();
                            if (!physicalThingStatementTypeData.includes(sampleMotivationConceptId)) {
                                physicalThingStatementTypeData = [sampleMotivationConceptId];
                            }
                        }
    
                        physicalThingStatementTile.data[physicalThingStatementTypeNodeId] = physicalThingStatementTypeData;
                        physicalThingStatementTile.transactionId = params.form.workflowId;

                        physicalThingStatementTile.save().then(function(data) {
                            resolve(data);
                        });
                    }
                    else {
                        resolve(null);
                    }
                });
            };

            const savePhysicalThingRemovedFromTile = function(samplePhysicalThingRemovedFromTile, removedFromResourceInstanceIds) {
                return new Promise(function(resolve, _reject) {
                    const physicalThingRemovedFromNodeId = '38814345-d2bd-11e9-b9d6-a4d18cec433a' // Removal from Object_Removed From (E22)
                    const tileDataObj = removedFromResourceInstanceIds.map(resourceId => 
                        ({
                            "resourceId": resourceId,
                            "resourceXresourceId": "",
                            "ontologyProperty": "",
                            "inverseOntologyProperty": ""
                        })
                    );
                    samplePhysicalThingRemovedFromTile.data[physicalThingRemovedFromNodeId](tileDataObj)
                    samplePhysicalThingRemovedFromTile.transactionId = params.form.workflowId;

                    samplePhysicalThingRemovedFromTile.save().then(function(data) {
                        resolve(data);
                    });
                });
            }

            self.savingTile(true);
            getRegionPhysicalThingNameCard().then(function(regionPhysicalThingNameCard) {
                var regionPhysicalThingNameTile = getWorkingTile(regionPhysicalThingNameCard);

                self.savingMessage(`Saving Sample Area Name ...`);
                savePhysicalThingNameTile(regionPhysicalThingNameTile, "region").then(function(regionPhysicalThingNameData) {
                    const physicalThingClassificationNodeId = '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a'; // type (E55)

                    StepUtils.saveThingToProject(regionPhysicalThingNameData.resourceinstance_id, params.projectSet, params.form.workflowId, self.physThingSearchResultsLookup).then(function() {

                    self.fetchCardFromResourceId(regionPhysicalThingNameData.resourceinstance_id, physicalThingClassificationNodeId).then(function(regionPhysicalThingClassificationCard) {
                        var physicalThingClassificationTile = getWorkingTile(regionPhysicalThingClassificationCard);

                        self.savingMessage(`Saving Sample Area Classification ...`);
                        savePhysicalThingClassificationTile(physicalThingClassificationTile, "region").then(function(regionPhysicalThingClassificationData) {
                            var physicalThingPartOfNodeId = 'f8d5fe4c-b31d-11e9-9625-a4d18cec433a'; // part of (E22)

                            self.fetchCardFromResourceId(regionPhysicalThingClassificationData.resourceinstance_id, physicalThingPartOfNodeId).then(function(regionPhysicalThingPartOfCard) {
                                var physicalThingPartOfTile = getWorkingTile(regionPhysicalThingPartOfCard);

                                self.savingMessage(`Saving Relationship between Sample Area and Parent (${params.physicalThingName}) ...`);
                                savePhysicalThingPartOfTile(physicalThingPartOfTile).then(function(regionPhysicalThingPartOfData) {
                                    self.fetchCardFromResourceId(self.samplingActivityResourceId, samplingUnitNodegroupId).then(function(samplingActivitySamplingUnitCard) {
                                        var samplingActivitySamplingUnitTile = getWorkingSamplingActivityUnitTile(samplingActivitySamplingUnitCard, regionPhysicalThingNameData);
                    
                                        getSamplePhysicalThingNameCard(samplingActivitySamplingUnitTile).then(function(samplePhysicalThingNameCard) {
                                            var samplePhysicalThingNameTile = getWorkingTile(samplePhysicalThingNameCard);

                                            self.savingMessage(`Saving Sample Name ...`);
                                            savePhysicalThingNameTile(samplePhysicalThingNameTile, "sample").then(function(samplePhysicalThingNameData) {
                                                const physicalThingRemovedFromNodegroupId = 'b11f217a-d2bc-11e9-8dfa-a4d18cec433a' // Removal from Object (E80)

                                                self.fetchCardFromResourceId(samplePhysicalThingNameData.resourceinstance_id, physicalThingPartOfNodeId).then(function(samplePhysicalThingPartOfCard){
                                                    const samplePhysicalThingPartOfTile = getWorkingTile(samplePhysicalThingPartOfCard);
                                                    self.savingMessage(`Saving Relationship between Sample and Parent (${params.physicalThingName}) ...`);
                                                    savePhysicalThingPartOfTile(samplePhysicalThingPartOfTile);
                                                });

                                                self.fetchCardFromResourceId(samplePhysicalThingNameData.resourceinstance_id, physicalThingRemovedFromNodegroupId).then(function(samplePhysicalThingRemovedFromCard){
                                                    const samplePhysicalThingRemovedFromTile = getWorkingTile(samplePhysicalThingRemovedFromCard);
                                                    const removedFromPhysicalThingResourceIds = [self.physicalThingResourceId, regionPhysicalThingNameData.resourceinstance_id];
                                                    self.savingMessage(`Saving Relationship between Sample and Sample Area ...`);
                                                    savePhysicalThingRemovedFromTile(samplePhysicalThingRemovedFromTile, removedFromPhysicalThingResourceIds);
                                                });

                                                self.savingMessage(`Saving Sample to the Project ...`);
                                                StepUtils.saveThingToProject(samplePhysicalThingNameData.resourceinstance_id, params.projectSet, params.form.workflowId, self.physThingSearchResultsLookup).then(function() {

                                                const physicalThingClassificationNodeId = '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a'; // type (E55)

                                                self.fetchCardFromResourceId(samplePhysicalThingNameData.resourceinstance_id, physicalThingClassificationNodeId).then(function(samplePhysicalThingClassificationCard) {
                                                    var physicalThingClassificationTile = getWorkingTile(samplePhysicalThingClassificationCard);
                            
                                                    self.savingMessage(`Saving Sample Classification ...`);
                                                    savePhysicalThingClassificationTile(physicalThingClassificationTile, "sample").then(function(samplePhysicalThingClassificationData) {
                                                        var physicalThingStatementNodegroupId = '1952bb0a-b498-11e9-a679-a4d18cec433a';  // Statement (E33)
                                                        
                                                        self.fetchCardFromResourceId(samplePhysicalThingClassificationData.resourceinstance_id, physicalThingStatementNodegroupId).then(function(physicalThingStatementCard) {
                                                            var physicalThingSampleDescriptionStatementTile = getWorkingPhysicalThingSamplingDescriptionTile(physicalThingStatementCard);

                                                            self.savingMessage(`Saving Sample Description ...`);
                                                            savePhysicalThingStatementTile(physicalThingSampleDescriptionStatementTile, "description").then(function(_physicalThingStatmentSampleDescriptionData) {
                                                                var physicalThingStatementNodegroupId = '1952bb0a-b498-11e9-a679-a4d18cec433a';  // Statement (E33)

                                                                self.fetchCardFromResourceId(samplePhysicalThingNameData.resourceinstance_id, physicalThingStatementNodegroupId).then(function(physicalThingStatementCard) {
                                                                    var physicalThingSamplingMotivationTile = getWorkingPhysicalThingSamplingMotivationTile(physicalThingStatementCard);

                                                                    self.savingMessage(`Saving Sample Motivation ...`);
                                                                    savePhysicalThingStatementTile(physicalThingSamplingMotivationTile, "motivation").then(function(_samplingActivitySamplingMotivationData) {
                                                                        self.savingMessage(`Saving Relationship between Sample and Sampling Activity ...`);
                                                                        saveSamplingActivitySamplingUnitTile(samplingActivitySamplingUnitTile, regionPhysicalThingNameData, samplePhysicalThingNameData).then(function(_samplingActivitySamplingUnitData) {
                                                                            self.savingMessage(`Saving Relationship between Sample Area and Parent (${params.physicalThingName}) ...`);
                                                                            saveSelectedSampleLocationInstance(regionPhysicalThingPartOfData).then(function(_selectedSampleLocationInstanceData) {
                                                                                // fetches again for updated data
                                                                                // self.fetchCardFromResourceId(self.samplingActivityResourceId, samplingUnitNodegroupId).then(function(updatedSamplingActivitySamplingUnitCard) {
                                                                                    updateAnnotations().then(function(_physicalThingAnnotationNode) {
                                                                                        self.samplingActivitySamplingUnitCard(samplingActivitySamplingUnitCard);
                                                                                        
                                                                                        self.updateSampleLocationInstances();
                                                                                        self.selectSampleLocationInstance(self.selectedSampleLocationInstance());
                            
                                                                                        self.savingTile(false);
                                                                                        self.savingMessage('');
                                                                                        params.dirty(true);
                                                                                        params.form.complete(true);

                                                                                        params.pageVm.alert("");
                                                                                        self.drawFeatures([]);
                                                                                    });
                                                                                // });
                                                                            });
                                                                        });
                                                                    });
                                                                });
                                                            });
                                                        });
                                                    });
                                                });
                                            });
                                        });
                                    });
                                });
                            });
                        });
                    });
                });
            });
        });
    });
};

        this.loadNewSampleLocationTile = function() {
            var newTile = self.card.getNewTile(true);  /* true flag forces new tile generation */
            self.selectSampleLocationInstance(newTile);
        };

        this.saveWorkflowStep = function() {
            params.form.complete(false);
            params.form.saving(true);
            let mappedInstances = self.sampleLocationInstances().map((instance) => { return { "data": instance.data }});
            params.form.savedData(mappedInstances);
            params.form.complete(true);
            params.form.saving(false);
        };

        this.loadExternalCardData = function(data) {
            var partIdentifierAssignmentNodeGroupId = 'fec59582-8593-11ea-97eb-acde48001122';  // Part Identifier Assignment (E13) 

            var partIdentifierAssignmentCardData = data.cards.find(function(card) {
                return card.nodegroup_id === partIdentifierAssignmentNodeGroupId;
            });

            var handlers = {
                'after-update': [],
                'tile-reset': []
            };

            var graphModel = new GraphModel({
                data: {
                    nodes: data.nodes,
                    nodegroups: data.nodegroups,
                    edges: []
                },
                datatypes: data.datatypes
            });

            var partIdentifierAssignmentCard = new CardViewModel({
                card: partIdentifierAssignmentCardData,
                graphModel: graphModel,
                tile: null,
                resourceId: ko.observable(self.physicalThingResourceId),
                displayname: ko.observable(data.displayname),
                handlers: handlers,
                cards: data.cards,
                tiles: data.tiles,
                cardwidgets: data.cardwidgets,
                userisreviewer: data.userisreviewer,
            });

            var card = partIdentifierAssignmentCard;
            var tile = partIdentifierAssignmentCard.getNewTile();

            self.card = card;
            self.tile = tile;

            params.card = self.card;
            params.tile = self.tile;
            
            var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)
            params.widgets = self.card.widgets().filter(function(widget) {
                return widget.node_id() === partIdentifierAssignmentPolygonIdentifierNodeId;
            });

            self.physicalThingPartIdentifierAssignmentCard(card);
            self.physicalThingPartIdentifierAssignmentTile(tile);

            const classificationNodeId = '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a';
            const analysisAreaTypeConceptId = '31d97bdd-f10f-4a26-958c-69cb5ab69af1';
            const related = card.tiles().map((tile) => {
                return {
                    'resourceid': ko.unwrap(tile.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId])[0].resourceId(),
                    'tileid': tile.tileid
                }
            });

            Promise.all(related.map(resource => ResourceUtils.lookupResourceInstanceData(resource.resourceid))).then((values) => {
                values.forEach((value) => {
                    self.physThingSearchResultsLookup[value._id] = value;
                    const nodevals = ResourceUtils.getNodeValues({
                        nodeId: classificationNodeId,
                        where: {
                            nodeId: classificationNodeId,
                            contains: analysisAreaTypeConceptId
                        }
                    }, value._source.tiles);
                    if (nodevals.includes(analysisAreaTypeConceptId)) {
                        self.analysisAreaResourceIds.push(related.find(tile => value._id === tile.resourceid));
                    }
                });
                card.tiles().forEach(tile => tile.samplingActivityResourceId = tile.samplingActivityResourceId ? tile.samplingActivityResourceId : ko.observable());
                self.sampleLocationInstances(card.tiles());
                self.analysisAreaTileIds = self.analysisAreaResourceIds.map(item => item.tileid);
            })
            /* 
                subscription to features lives here because we _only_ want it to run once, on blank starting tile, when a user places a feature on the map
            */
            var tileFeatureGeometrySubscription = tile.data[partIdentifierAssignmentPolygonIdentifierNodeId].subscribe(function(data) {
                if (data) {
                    self.selectSampleLocationInstance(tile);
                    tileFeatureGeometrySubscription.dispose();
                }
            });

            self.hasExternalCardData(true);
        };

        this.handleExternalCardData = function() {
            var partIdentifierAssignmentLabelNodeId = '3e541cc6-859b-11ea-97eb-acde48001122';
            self.partIdentifierAssignmentLabelWidget(self.card.widgets().find(function(widget) {
                return ko.unwrap(widget.node_id) === partIdentifierAssignmentLabelNodeId;
            }));

            var partIdentifierAssignmentPolygonIdentifierNodeId = '97c30c42-8594-11ea-97eb-acde48001122';
            self.partIdentifierAssignmentPolygonIdentifierWidget(self.card.widgets().find(function(widget) {
                return ko.unwrap(widget.node_id) === partIdentifierAssignmentPolygonIdentifierNodeId;
            }));                
            
            IIIFAnnotationViewmodel.apply(self, [{
                ...params,
                hideEditorTab: ko.observable(true),
                onEachFeature: function(feature, layer) {
                    var featureLayer = self.featureLayers().find(function(featureLayer) {
                        return featureLayer.feature.id === layer.feature.id;
                    });

                    if (!featureLayer) {
                        self.featureLayers.push(layer)
                    }

                    if (self.analysisAreaTileIds.includes(feature.properties.tileId)){
                        const analysisArea = self.analysisAreaResourceIds.find(analysisArea => analysisArea.tileid === feature.properties.tileId);
                        var popup = L.popup({
                            closeButton: false,
                            maxWidth: 349
                        })
                            .setContent(iiifPopup)
                            .on('add', function() {
                                var popupData = {
                                    'closePopup': function() {
                                        popup.remove();
                                    },
                                    'name': ko.observable(''),
                                    'description': ko.observable(''),
                                    'graphName': feature.properties.graphName,
                                    'resourceinstanceid': analysisArea.resourceid,
                                    'reportURL': arches.urls.resource_report
                                };
                                window.fetch(arches.urls.resource_descriptors + popupData.resourceinstanceid)
                                    .then(function(response) {
                                        return response.json();
                                    })
                                    .then(function(descriptors) {
                                        popupData.name(descriptors.displayname);
                                        const description = `<strong>Analysis Area</strong>
                                            <br>Analysis Areas may not be modified in the sample taking workflow
                                            <br>${descriptors['map_popup'] !== "Undefined" ? descriptors['map_popup'] : ''}`
                                        popupData.description(description);
                                    });
                                var popupElement = popup.getElement()
                                    .querySelector('.mapboxgl-popup-content');
                                ko.applyBindingsToDescendants(popupData, popupElement);
                            });
                        layer.bindPopup(popup);
                    }

                    layer.on({

                        click: function() {              
                            const sampleLocationInstance = self.getSampleLocationTileFromFeatureId(feature.id);
                            
                            if (sampleLocationInstance && !self.analysisAreaTileIds.includes(sampleLocationInstance.tileid)) {
                                self.drawFeatures([]);
                                self.featureClick = true;

                                if (!self.selectedSampleLocationInstance() || self.selectedSampleLocationInstance().tileid !== sampleLocationInstance.tileid ) {
                                    self.selectSampleLocationInstance(sampleLocationInstance);
                                }
                                else {
                                    self.tile.reset();
                                    self.resetCanvasFeatures();
    
                                    const selectedFeature = ko.toJS(self.selectedSampleLocationInstanceFeatures().find(function(selectedSampleLocationInstanceFeature) {
                                        return ko.unwrap(selectedSampleLocationInstanceFeature.id) === feature.id;
                                    }));
    
                                    self.selectedFeature(selectedFeature);
                                    if(self.selectedSampleRelatedSamplingActivity() == self.samplingActivityResourceId)
                                    {
                                        self.removeFeatureFromCanvas(self.selectedFeature());
                                        self.drawFeatures([selectedFeature]);
                                    } else {
                                        self.highlightAnnotation()
                                    }
                                } 
                            }
                        },
                    })
                },
                buildAnnotationNodes: function(json) {
                    editNodeActiveState = ko.observable(true);
                    nonEditNodeActiveState = ko.observable(true);
                    editNodeActiveState.subscribe(function(active){
                        if (!active) {
                            self.resetSampleLocationTile();
                            updateAnnotations();
                        }
                    });
                    var updateAnnotations = function() {
                        let sampleAnnotations = ko.observableArray();
                        let analysisAreaAnnotations = ko.observableArray();
                        var canvas = self.canvas();
                        if (canvas) {
                            window.fetch(arches.urls.iiifannotations + '?canvas=' + canvas + '&nodeid=' + partIdentifierAssignmentPolygonIdentifierNodeId)
                                .then(function(response) {
                                    return response.json();
                                })
                                .then(function(json) {
                                    json.features.forEach(function(feature) {
                                        feature.properties.graphName = "Physical Thing";
                                        if (self.analysisAreaTileIds.includes(feature.properties.tileId)) {
                                            feature.properties.type = 'analysis_area';
                                            feature.properties.color = '#999999';
                                            feature.properties.fillColor = '#999999';
                                            analysisAreaAnnotations.push(feature);
                                        } else {
                                            feature.properties.type = 'sample_location';
                                            sampleAnnotations.push(feature);
                                        }
                                    });
                                    self.annotationNodes([
                                        {
                                            name: "Sample Locations",
                                            icon: "fa fa-eyedropper",
                                            active: editNodeActiveState,
                                            opacity: ko.observable(100),
                                            annotations: sampleAnnotations
                                        },
                                        {
                                            name: "Analysis Areas",
                                            icon: "fa fa-eye",
                                            active: nonEditNodeActiveState,
                                            opacity: ko.observable(100),
                                            annotations: analysisAreaAnnotations
                                        },
                                    ])
                                    self.highlightAnnotation();
                                });
                        }
                    };
                    self.canvas.subscribe(updateAnnotations);
                    updateAnnotations();
                }
            }]);

            /* overwrites iiif-annotation method */ 
            self.updateTiles = function() {
                _.each(self.featureLookup, function(value) {
                    value.selectedTool(null);
                });

                var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)

                var tileFeatures = ko.toJS(self.tile.data[partIdentifierAssignmentPolygonIdentifierNodeId].features);

                if (tileFeatures) {
                    var featuresNotInTile = self.drawFeatures().filter(function(drawFeature) {
                        return !tileFeatures.find(function(tileFeature) {
                            return tileFeature.id === drawFeature.id;
                        });
                    });

                    self.drawFeatures().forEach(function(drawFeature) {
                        var editedFeatureIndex = tileFeatures.findIndex(function(feature) {
                            return feature.id === drawFeature.id;
                        });

                        if (editedFeatureIndex > -1) {
                            tileFeatures[editedFeatureIndex] = drawFeature;
                        }
                    });

                    self.tile.data[partIdentifierAssignmentPolygonIdentifierNodeId].features([...tileFeatures, ...featuresNotInTile]);
                }
                else {
                    self.widgets.forEach(function(widget) {
                        var id = ko.unwrap(widget.node_id);
                        var features = [];
                        self.drawFeatures().forEach(function(feature){
                            if (feature.properties.nodeId === id) {
                                features.push(feature);
                            }
                        });
                        if (ko.isObservable(self.tile.data[id])) {
                            self.tile.data[id]({
                                type: 'FeatureCollection',
                                features: features
                            });
                        } 
                        else {
                            self.tile.data[id].features(features);
                        }
                    });
                }
            };

                        
            self.deleteFeature = function(feature) {
                /* BEGIN update table */ 
                var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)

                var selectedSampleLocationInstance = self.selectedSampleLocationInstance();
                var selectedSampleLocationInstanceFeaturesNode = ko.unwrap(selectedSampleLocationInstance.data[partIdentifierAssignmentPolygonIdentifierNodeId]);

                if (selectedSampleLocationInstanceFeaturesNode) {
                    var updatedSelectedSampleLocationInstanceFeatures = ko.unwrap(selectedSampleLocationInstanceFeaturesNode.features).filter(function(selectedFeature) {
                        return ko.unwrap(selectedFeature.id) !== ko.unwrap(feature.id);
                    });
                    
                    if (ko.isObservable(selectedSampleLocationInstanceFeaturesNode.features)) {
                        selectedSampleLocationInstanceFeaturesNode.features(updatedSelectedSampleLocationInstanceFeatures);
                    }
                    else {
                        selectedSampleLocationInstanceFeaturesNode.features = ko.observableArray(updatedSelectedSampleLocationInstanceFeatures);
                    }

                    selectedSampleLocationInstance.data[partIdentifierAssignmentPolygonIdentifierNodeId] = selectedSampleLocationInstanceFeaturesNode;
                }

                self.selectedSampleLocationInstance(selectedSampleLocationInstance);
                /* END update table */ 

                /* BEGIN update canvas */ 
                self.removeFeatureFromCanvas(feature);

                var drawFeature = self.drawFeatures().find(function(drawFeature) {
                    return ko.unwrap(drawFeature.id) === ko.unwrap(feature.id);
                });

                if (drawFeature) {
                    self.drawFeatures([]);
                }
                /* END update canvas */ 
            }

            self.editFeature = function(feature) {
                self.featureLayers().forEach(function(featureLayer) {
                    if (featureLayer.feature.id === ko.unwrap(feature.id)) {
                        featureLayer.fireEvent('click');
                    }
                });
            };

            self.drawLayer.subscribe(function(drawLayer) {
                drawLayer.getLayers().forEach(function(layer) {
                    layer.editing.enable();
                    layer.setStyle({color: '#BCFE2B', fillColor: '#BCFE2B'});
                });
            });
        };

        this.clearEditedGeometries = function() {
            if (self.tile.tileid && self.selectedFeature()) {
                self.resetSampleLocationTile();
            }
        };

        this.fetchCardFromResourceId = function(resourceId, nodegroupId) {
            return new Promise(function(resolve, _reject) {
                self._fetchCard(resourceId, null, nodegroupId).then(function(data) {
                    resolve(data);
                });
            });
        };

        this.fetchCardFromGraphId = function(graphId, nodegroupId) {
            return new Promise(function(resolve, _reject) {
                self._fetchCard(null, graphId, nodegroupId).then(function(data) {
                    resolve(data);
                });
            });
        };

        this._fetchCard = function(resourceId, graphId, nodegroupId) {
            return new Promise(function(resolve, _reject) {
                $.getJSON( arches.urls.api_card + ( resourceId || graphId ) ).then(function(data) {
                    var cardData = data.cards.find(function(card) {
                        return card.nodegroup_id === nodegroupId;
                    });

                    var handlers = {
                        'after-update': [],
                        'tile-reset': []
                    };
        
                    var graphModel = new GraphModel({
                        data: {
                            nodes: data.nodes,
                            nodegroups: data.nodegroups,
                            edges: []
                        },
                        datatypes: data.datatypes
                    });

                    resolve(new CardViewModel({
                        card: cardData,
                        graphModel: graphModel,
                        tile: null,
                        resourceId: ko.observable(ko.unwrap(resourceId)),
                        displayname: ko.observable(data.displayname),
                        handlers: handlers,
                        cards: data.cards,
                        tiles: data.tiles,
                        cardwidgets: data.cardwidgets,
                        userisreviewer: data.userisreviewer,
                    }));

                });
            });
        };

        ko.bindingHandlers.scrollTo = {
            update: function (element, valueAccessor) {
                var _value = valueAccessor();
                var _valueUnwrapped = ko.unwrap(_value);
                if (_valueUnwrapped) {
                    element.scrollIntoView({behavior: "smooth", block: "center", inline: "nearest"});
                }
            }
        };

        this.initialize();
    };

    ko.components.register('sample-taking-sample-location-step', {
        viewModel: viewModel,
        template: { require: 'text!templates/views/components/workflows/sample-taking-workflow/sample-taking-sample-location-step.htm' }
    });
    return viewModel;
});
