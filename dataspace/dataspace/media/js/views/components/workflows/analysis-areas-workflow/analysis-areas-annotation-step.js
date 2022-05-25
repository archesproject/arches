define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'views/components/workflows/stepUtils',
    'utils/resource',
    'models/graph',
    'viewmodels/card',
    'views/components/iiif-annotation',
    'text!templates/views/components/iiif-popup.htm',
    'views/components/resource-instance-nodevalue',
], function(_, $, arches, ko, koMapping, StepUtils, ResourceUtils, GraphModel, CardViewModel, IIIFAnnotationViewmodel, iiifPopup) {
    function viewModel(params) {
        var self = this;
        _.extend(this, params);

        this.physicalThingResourceId = koMapping.toJS(params.physicalThingResourceId);
        
        var digitalResourceServiceIdentifierContentNodeId = '56f8e9bd-ca7c-11e9-b578-a4d18cec433a';
        const partIdentifierAssignmentPhysicalPartOfObjectNodeId = 'b240c366-8594-11ea-97eb-acde48001122'; 
        const physicalThingPartAnnotationNodeId = "97c30c42-8594-11ea-97eb-acde48001122";
        this.allFeatureIds = [];
        this.sampleLocationResourceIds = [];
        this.manifestUrl = ko.observable(params.imageStepData[digitalResourceServiceIdentifierContentNodeId]);

        this.savingTile = ko.observable();
        this.savingMessage = ko.observable();
        this.physThingSearchResultsLookup = {};

        this.selectedFeature = ko.observable();
        this.featureLayers = ko.observableArray();
        this.isFeatureBeingEdited = ko.observable(false);

        this.physicalThingPartIdentifierAssignmentCard = ko.observable();
        this.physicalThingPartIdentifierAssignmentTile = ko.observable();

        this.partIdentifierAssignmentLabelWidget = ko.observable();
        this.partIdentifierAssignmentPolygonIdentifierWidget = ko.observable();
        this.partIdentifierAssignmentAnnotatorWidget = ko.observable();

        this.activeTab = ko.observable();
        this.hasExternalCardData = ko.observable(false);

        this.analysisAreaInstances = ko.observableArray();
        
        this.selectedAnalysisAreaInstance = ko.observable();

        this.switchCanvas = function(tile){
            const features = ko.unwrap(tile.data[physicalThingPartAnnotationNodeId].features);
            const canvasPath = features?.[0]?.properties.canvas();
            if (self.canvas() !== canvasPath) {
                var canvas = self.canvases().find(c => c.images[0].resource.service['@id'] === canvasPath);
                if (canvas) {
                    self.canvasClick(canvas);       
                }
            }
        };

        this.selectedAnalysisAreaInstance.subscribe(function(selectedAnalysisAreaInstance) {
            self.highlightAnnotation();

            if (selectedAnalysisAreaInstance) {
                self.tile = selectedAnalysisAreaInstance;
                params.tile = selectedAnalysisAreaInstance;
                self.physicalThingPartIdentifierAssignmentTile(selectedAnalysisAreaInstance);
                if (ko.unwrap(selectedAnalysisAreaInstance.data[physicalThingPartAnnotationNodeId])?.features) {
                    self.switchCanvas(selectedAnalysisAreaInstance)
                }
            }
        });

        this.tileDirty = ko.computed(function() {
            if (self.physicalThingPartIdentifierAssignmentTile()) {
                return self.physicalThingPartIdentifierAssignmentTile().dirty();
            }
        });
                
        this.selectedAnalysisAreaInstanceFeatures = ko.computed(function() {
            var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)

            if (self.selectedAnalysisAreaInstance()) {
                if (ko.unwrap(self.selectedAnalysisAreaInstance().data[partIdentifierAssignmentPolygonIdentifierNodeId])) {
                    var partIdentifierAssignmentPolygonIdentifierData = ko.unwrap(self.selectedAnalysisAreaInstance().data[partIdentifierAssignmentPolygonIdentifierNodeId]);
                    return ko.unwrap(partIdentifierAssignmentPolygonIdentifierData.features);
                }
            }
        });

        this.analysisAreaFilterTerm = ko.observable();
        this.filteredAnalysisAreaInstances = ko.computed(function() {
            const analysisAreasOnly = self.analysisAreaInstances().filter(function(a){
                const sampleLocationResourceIds = self.sampleLocationResourceIds.map(item => item.resourceid);
                const partId = ko.unwrap(a.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId]()[0].resourceId)
                return !sampleLocationResourceIds.includes(partId);
            });
            self.analysisAreasOnlySnapshot = analysisAreasOnly.map(tile => tile.tileid);
            if (self.analysisAreaFilterTerm()) {
                return analysisAreasOnly.filter(function(analysisAreaInstance) {
                    var partIdentifierAssignmentLabelNodeId = '3e541cc6-859b-11ea-97eb-acde48001122';
                    return analysisAreaInstance.data[partIdentifierAssignmentLabelNodeId]().includes(self.analysisAreaFilterTerm());
                });
            }
            else {
                return analysisAreasOnly;
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

        this.physicalThingName = ko.observable();
        window.fetch(arches.urls.api_resources(self.physicalThingResourceId) + '?format=json&compact=false&v=beta')
        .then(function(response){
            if(response.ok){
                return response.json();
            }
        })
        .then(function(data){
            self.physicalThingName(data.displayname);
        })

        this.areaName = ko.computed(function(){
            var partIdentifierAssignmentLabelNodeId = '3e541cc6-859b-11ea-97eb-acde48001122';
            if (self.selectedAnalysisAreaInstance()){
                const baseName = ko.unwrap(self.selectedAnalysisAreaInstance().data[partIdentifierAssignmentLabelNodeId]) || "";
                return `${baseName} [Region of ${self.physicalThingName()}]`;
            }
        })

        this.initialize = function() {
            $.getJSON(arches.urls.api_card + self.physicalThingResourceId).then(function(data) {
                self.loadExternalCardData(data);
            });
        };

        this.getAnalysisAreaTileFromFeatureId = function(featureId) {
            var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)

            return self.analysisAreaInstances().find(function(analysisAreaInstance) {
                var analysisAreaInstanceFeatures = analysisAreaInstance.data[partIdentifierAssignmentPolygonIdentifierNodeId].features();

                return analysisAreaInstanceFeatures.find(function(analysisAreaInstanceFeature) {
                    return ko.unwrap(analysisAreaInstanceFeature.id) === featureId;
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

                                    if (self.selectedAnalysisAreaInstance() && self.selectedAnalysisAreaInstance().tileid === feature.feature.properties.tileId) {
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
            
            var physicalThingAnnotationNodeName = "Analysis Areas";
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
            
            if (self.selectedAnalysisAreaInstanceFeatures()) {
                var physicalThingAnnotationNodeName = "Analysis Areas";
                var physicalThingAnnotationNode = annotationNodes.find(function(annotationNode) {
                    return annotationNode.name === physicalThingAnnotationNodeName;
                });
    
                var physicalThingAnnotationNodeAnnotationIds = physicalThingAnnotationNode.annotations().map(function(annotation) {
                    return ko.unwrap(annotation.id);
                });
                
                var unaddedSelectedAnalysisAreaInstanceFeatures = self.selectedAnalysisAreaInstanceFeatures().reduce(function(acc, feature) {
                    if (!physicalThingAnnotationNodeAnnotationIds.includes(ko.unwrap(feature.id)) &&
                        feature.properties.canvas === self.canvas) {
                        feature.properties.tileId = self.selectedAnalysisAreaInstance().tileid;
                        acc.push(ko.toJS(feature));
                    }
                    return acc;
                }, []);
    
                physicalThingAnnotationNode.annotations([...physicalThingAnnotationNode.annotations(), ...unaddedSelectedAnalysisAreaInstanceFeatures]);
    
                var physicalThingAnnotationNodeIndex = annotationNodes.findIndex(function(annotationNode) {
                    return annotationNode.name === physicalThingAnnotationNodeName;
                });
    
                annotationNodes[physicalThingAnnotationNodeIndex] = physicalThingAnnotationNode;
            }

            self.annotationNodes(annotationNodes);
        };

        this.updateAnalysisAreaInstances = function() {
            canvasids = self.canvases().map(canvas => canvas.images[0].resource['@id'])
            const tilesBelongingToManifest = self.card.tiles().filter(
                tile => canvasids.find(
                    canvas => canvas.startsWith(tile.data[physicalThingPartAnnotationNodeId].features()[0].properties.canvas())
                    )
                );
            
            self.analysisAreaInstances(tilesBelongingToManifest);
        };

        this.selectAnalysisAreaInstance = function(analysisAreaInstance) {
            var previouslySelectedAnalysisAreaInstance = self.selectedAnalysisAreaInstance();
            
            if (previouslySelectedAnalysisAreaInstance && previouslySelectedAnalysisAreaInstance.tileid !== analysisAreaInstance.tileid) {
                /* resets any changes not explicity saved to the tile */ 
                previouslySelectedAnalysisAreaInstance.reset();

                self.drawFeatures([]);
                self.resetCanvasFeatures();
            }

            if (self.physicalThingPartIdentifierAssignmentTile()) {
                self.physicalThingPartIdentifierAssignmentTile().reset();
            }
            
            self.selectedAnalysisAreaInstance(analysisAreaInstance);

        };

        this.resetAnalysisAreasTile = function() {
            self.tile.reset();
            self.resetCanvasFeatures();
            self.drawFeatures([]);
            self.highlightAnnotation();
            self.selectedFeature(null);
        };

        this.setPhysicalThingGeometriesToVisible = function(annotationNodes) {
            var physicalThingAnnotationNodeName = "Analysis Areas";
            var physicalThingAnnotationNode = annotationNodes.find(function(annotationNode) {
                return annotationNode.name === physicalThingAnnotationNodeName;
            });

            physicalThingAnnotationNode.active(true); 
            self.updateAnalysisAreaInstances();
        };

        this.saveAnalysisAreaTile = function() {
            var savePhysicalThingNameTile = function(physicalThingNameTile) {
                return new Promise(function(resolve, _reject) {
                    var physicalThingNameContentNodeId = 'b9c1d8a6-b497-11e9-876b-a4d18cec433a'; // Name_content (xsd:string)
                    physicalThingNameTile.data[physicalThingNameContentNodeId] = self.areaName();
                    physicalThingNameTile.transactionId = params.form.workflowId;

                    physicalThingNameTile.save().then(function(physicalThingNameData) {
                        resolve(physicalThingNameData);
                    });
                });
            };

            const savePhysicalThingClassificationTile = function(physicalThingClassificationTile) {
                const analysisAreaTypeConceptId = '31d97bdd-f10f-4a26-958c-69cb5ab69af1';
                return new Promise(function(resolve, _reject) {
                    const physicalThingClassificationNodeId = '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a'; // type (E55)
                    physicalThingClassificationTile.data[physicalThingClassificationNodeId] = [analysisAreaTypeConceptId];
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

            var updateSelectedAnalysisAreaInstance = function(physicalThingPartOfData) {
                return new Promise(function(resolve, _reject) {
                    /* assigns Physical Thing to be the Part Identifier on the parent selected Physical Thing  */ 
                    var physicalThingPartOfNodeId = 'f8d5fe4c-b31d-11e9-9625-a4d18cec433a'; // part of (E22)
                    var physicalThingPartOfResourceXResourceId = physicalThingPartOfData.data[physicalThingPartOfNodeId][0]['resourceXresourceId'];
                    
                    var selectedAnalysisAreaInstance = self.selectedAnalysisAreaInstance();
                    
                    var partIdentifierAssignmentPhysicalPartOfObjectNodeId = 'b240c366-8594-11ea-97eb-acde48001122';   
    
                    selectedAnalysisAreaInstance.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId]([{
                        "resourceId": physicalThingPartOfData.resourceinstance_id,
                        "resourceXresourceId": physicalThingPartOfResourceXResourceId,
                        "ontologyProperty": "",
                        "inverseOntologyProperty": ""
                    }]);
                    
                    selectedAnalysisAreaInstance.transactionId = params.form.workflowId;

                    selectedAnalysisAreaInstance.save().then(function(data) {
                        resolve(data);
                    }).catch(exc => {
                        params.pageVm.alert("");
                        if(/This card requires values for the following\: Name for Part/.test(exc.responseJSON.message)) {
                            params.pageVm.alert(new params.form.AlertViewModel('ep-alert-red', "Name required", "Providing a name is required"));
                        }
                        if(/This card requires values for the following\: Geometric Annotation/.test(exc.responseJSON.message)) {
                            params.pageVm.alert(new params.form.AlertViewModel('ep-alert-red', "Geometry required", "Providing a geometric annotation is required"));
                        }
                        self.savingTile(false);
                    })
                });
            };

            var updateAnnotations = function() {
                return new Promise(function(resolve, _reject) {
                    /* updates selected annotations */ 
                    var physicalThingAnnotationNodeName = "Analysis Areas";
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

            var getRegionPhysicalThingNameCard = function() {
                return new Promise(function(resolve, _reject) {
                    var physicalThingNameNodegroupId = 'b9c1ced7-b497-11e9-a4da-a4d18cec433a';  // Name (E33)
                    var partIdentifierAssignmentPhysicalPartOfObjectNodeId = 'b240c366-8594-11ea-97eb-acde48001122';       
                    var partIdentifierAssignmentPhysicalPartOfObjectData = ko.unwrap(self.tile.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId]);
        
                    if (partIdentifierAssignmentPhysicalPartOfObjectData) { /* if editing Physical Thing */
                        var partIdentifierAssignmentPhysicalPartOfObjectResourceId = ko.unwrap(partIdentifierAssignmentPhysicalPartOfObjectData[0]['resourceId']);
        
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

            self.savingTile(true);
            params.form.lockExternalStep('image-step', true);

            getRegionPhysicalThingNameCard().then(function(regionPhysicalThingNameCard) {
                const regionPhysicalThingNameTile = getWorkingTile(regionPhysicalThingNameCard);

                self.savingMessage(`Saving Analysis Area Name ...`);
                savePhysicalThingNameTile(regionPhysicalThingNameTile).then(function(physicalThingNameData) {
                    const physicalThingClassificationNodeId = '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a';

                    self.savingMessage(`Saving Analysis Area to the Project ...`);
                    StepUtils.saveThingToProject(physicalThingNameData.resourceinstance_id, params.projectSet, params.form.workflowId, self.physThingSearchResultsLookup).then(function() {

                        self.fetchCardFromResourceId(physicalThingNameData.resourceinstance_id, physicalThingClassificationNodeId).then(function(regionPhysicalThingClassificationCard) {
                           const regionPhysicalThingPartOfTile = getWorkingTile(regionPhysicalThingClassificationCard);
    
                           self.savingMessage(`Saving Analysis Area Classification ...`);
                           savePhysicalThingClassificationTile(regionPhysicalThingPartOfTile).then(function(physicalThingClassificationData) {
                                const physicalThingPartOfNodeId = 'f8d5fe4c-b31d-11e9-9625-a4d18cec433a'; // part of (E22)
                
                                self.fetchCardFromResourceId(physicalThingClassificationData.resourceinstance_id, physicalThingPartOfNodeId).then(function(regionPhysicalThingPartOfCard) {
                                    const regionPhysicalThingPartOfTile = getWorkingTile(regionPhysicalThingPartOfCard);
    
                                    self.savingMessage(`Saving Relationship between Analysis Area and Parent (${self.physicalThingName()}) ...`);
                                    savePhysicalThingPartOfTile(regionPhysicalThingPartOfTile).then(function(regionPhysicalThingPartOfData) {
                                        self.savingMessage(`Updating Relationship between Analysis Area and Parent (${self.physicalThingName()}) ...`);
                                        updateSelectedAnalysisAreaInstance(regionPhysicalThingPartOfData).then(function(_data) {
                                            self.savingMessage(`Updating Annotations ...`);
                                            updateAnnotations().then(function(_physicalThingAnnotationNode) {
                                                self.updateAnalysisAreaInstances();
                
                                                self.selectAnalysisAreaInstance(self.selectedAnalysisAreaInstance());
                                                self.savingTile(false);
                                                self.savingMessage('');
                                                params.pageVm.alert("");
                                                self.drawFeatures([]);
                                                let mappedInstances = self.analysisAreaInstances().map((instance) => { return { "data": instance.data }});
                                                params.form.savedData({
                                                    data: koMapping.toJS(mappedInstances),
                                                    currentAnalysisAreas: self.analysisAreasOnlySnapshot,
                                                });
                                                params.form.value(params.form.savedData());
                                                params.form.complete(true);
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

        this.loadNewAnalysisAreaTile = function() {
            if (!self.selectedAnalysisAreaInstance() || self.selectedAnalysisAreaInstance().tileid) {
                var newTile = self.card.getNewTile(true);  /* true flag forces new tile generation */
                self.selectAnalysisAreaInstance(newTile);
            }
        };

        this.identifySampleLocations = function(card) {
            const classificationNodeId = '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a';
            const sampleAreaTypeConceptId = '7375a6fb-0bfb-4bcf-81a3-6180cdd26123';
            const related = card.tiles().map((tile) => {
                return {
                    'resourceid': ko.unwrap(tile.data[partIdentifierAssignmentPhysicalPartOfObjectNodeId])[0].resourceId(),
                    'tileid': tile.tileid
                }
            });
            return Promise.all(related.map(resource => ResourceUtils.lookupResourceInstanceData(resource.resourceid))).then((values) => {
                values.forEach((value) => {
                    const nodevals = ResourceUtils.getNodeValues({
                        nodeId: classificationNodeId,
                        where: {
                            nodeId: classificationNodeId,
                            contains: sampleAreaTypeConceptId
                        }
                    }, value._source.tiles);
                    if (nodevals.includes(sampleAreaTypeConceptId)) {
                        self.sampleLocationResourceIds.push(related.find(tile => value._id === tile.resourceid));
                    }
                });
            });
        }

        this.loadExternalCardData = async function(data) {
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

            await this.identifySampleLocations(params.card);
            this.sampleLocationTileIds = self.sampleLocationResourceIds.map(item => item.tileid);

            var partIdentifierAssignmentPolygonIdentifierNodeId = "97c30c42-8594-11ea-97eb-acde48001122";  // Part Identifier Assignment_Polygon Identifier (E42)
            params.widgets = self.card.widgets().filter(function(widget) {
                return widget.node_id() === partIdentifierAssignmentPolygonIdentifierNodeId;
            });

            self.physicalThingPartIdentifierAssignmentCard(card);
            self.physicalThingPartIdentifierAssignmentTile(tile);

            /* 
                subscription to features lives here because we _only_ want it to run once, on blank starting tile, when a user places a feature on the map
            */
            var tileFeatureGeometrySubscription = tile.data[partIdentifierAssignmentPolygonIdentifierNodeId].subscribe(function(data) {
                if (data) {
                    self.selectAnalysisAreaInstance(tile);
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
            
            var partIdentifierAssignmentAnnotatorNodeId = 'a623eaf4-8599-11ea-97eb-acde48001122';
            self.partIdentifierAssignmentAnnotatorWidget(self.card.widgets().find(function(widget) {
                return ko.unwrap(widget.node_id) === partIdentifierAssignmentAnnotatorNodeId;
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

                    if (self.sampleLocationTileIds.includes(feature.properties.tileId)){
                        const sampleLocation = self.sampleLocationResourceIds.find(sampleLocation => sampleLocation.tileid === feature.properties.tileId);
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
                                    'resourceinstanceid': sampleLocation.resourceid,
                                    'reportURL': arches.urls.resource_report
                                };
                                window.fetch(arches.urls.resource_descriptors + popupData.resourceinstanceid)
                                    .then(function(response) {
                                        return response.json();
                                    })
                                    .then(function(descriptors) {
                                        popupData.name(descriptors.displayname);
                                        const description = `<strong>Sample Location</strong>
                                            <br>Sample locations may not be modified in the analysis area workflow
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
                        click: function(e) {
                            var analysisAreaInstance = self.getAnalysisAreaTileFromFeatureId(feature.id);
                            if (analysisAreaInstance && !self.sampleLocationTileIds.includes(analysisAreaInstance.tileid)) {
                                self.featureClick = true;
                                self.drawFeatures([]);
                                if (!self.selectedAnalysisAreaInstance() || self.selectedAnalysisAreaInstance().tileid !== analysisAreaInstance.tileid) {
                                    self.selectAnalysisAreaInstance(analysisAreaInstance);
                                }
                                else {
                                    self.tile.reset();
                                    self.resetCanvasFeatures();
    
                                    var selectedFeature = ko.toJS(self.selectedAnalysisAreaInstanceFeatures().find(function(selectedAnalysisAreaInstanceFeature) {
                                        return ko.unwrap(selectedAnalysisAreaInstanceFeature.id) === feature.id;
                                    }));
    
                                    self.selectedFeature(selectedFeature);
                                    self.removeFeatureFromCanvas(self.selectedFeature());
    
                                    self.drawFeatures([selectedFeature]);
                                } 
                            }
                        },
                    })
                },
                buildAnnotationNodes: function(json) {
                    const editNodeActiveState = ko.observable(true);
                    const nonEditNodeActiveState = ko.observable(true);
                    editNodeActiveState.subscribe(function(active){
                        if (!active) {
                            self.resetAnalysisAreasTile();
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
                                        if (self.sampleLocationTileIds.includes(feature.properties.tileId)) {
                                            feature.properties.type = 'sample_location';
                                            feature.properties.color = '#999999';
                                            feature.properties.fillColor = '#999999';
                                            sampleAnnotations.push(feature);
                                        } else {
                                            feature.properties.type = 'analysis_area';
                                            analysisAreaAnnotations.push(feature);
                                        }
                                    });
                                    self.annotationNodes([
                                        {
                                            name: "Analysis Areas",
                                            icon: "fa fa-eye",
                                            active: editNodeActiveState,
                                            opacity: ko.observable(100),
                                            annotations: analysisAreaAnnotations
                                        },
                                        {
                                            name: "Sample Locations",
                                            icon: "fa fa-eyedropper",
                                            active: nonEditNodeActiveState,
                                            opacity: ko.observable(100),
                                            annotations: sampleAnnotations
                                        }
                                    ])
                                    self.highlightAnnotation();
                                });
                        }
                    };
                    self.canvas.subscribe(updateAnnotations);
                    updateAnnotations();
                }
            }]);

            /* overwrites iiif-annotation methods */ 
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

                var selectedAnalysisAreaInstance = self.selectedAnalysisAreaInstance();
                var selectedAnalysisAreaInstanceFeaturesNode = ko.unwrap(selectedAnalysisAreaInstance.data[partIdentifierAssignmentPolygonIdentifierNodeId]);

                if (selectedAnalysisAreaInstanceFeaturesNode) {
                    var updatedSelectedAnalysisAreaInstanceFeatures = ko.unwrap(selectedAnalysisAreaInstanceFeaturesNode.features).filter(function(selectedFeature) {
                        return ko.unwrap(selectedFeature.id) !== ko.unwrap(feature.id);
                    });
                    
                    if (ko.isObservable(selectedAnalysisAreaInstanceFeaturesNode.features)) {
                        selectedAnalysisAreaInstanceFeaturesNode.features(updatedSelectedAnalysisAreaInstanceFeatures);
                    }
                    else {
                        selectedAnalysisAreaInstanceFeaturesNode.features = ko.observableArray(updatedSelectedAnalysisAreaInstanceFeatures);
                    }

                    selectedAnalysisAreaInstance.data[partIdentifierAssignmentPolygonIdentifierNodeId] = selectedAnalysisAreaInstanceFeaturesNode;
                }

                self.selectedAnalysisAreaInstance(selectedAnalysisAreaInstance);
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
                self.resetAnalysisAreasTile();
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
    }

    ko.components.register('analysis-areas-annotation-step', {
        viewModel: viewModel,
        template: { require: 'text!templates/views/components/workflows/analysis-areas-workflow/analysis-areas-annotation-step.htm' }
    });
    return viewModel;
});