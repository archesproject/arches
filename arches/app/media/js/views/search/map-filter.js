define(['jquery', 
    'jquery-ui',
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'views/map',
    'openlayers', 
    'knockout',
    'map/resource-layer-model',
    'utils',
    'resource-types',
    'plugins/supercluster/supercluster'], 
    function($, jqui, _, Backbone, bootstrap, arches, MapView, ol, ko, ResourceLayerModel, utils, resourceTypes, supercluster) {
        
        SHOW_NON_RESULT_MARKERS = false;
        var geoJSON = new ol.format.GeoJSON();
        return Backbone.View.extend({
            previousEntityIdArray: [],

            events: {
                'click .layer-zoom': 'layerZoom',
                'click .cluster-item-link': 'clusterItemClick'
            },

            initialize: function(options) { 
                var self = this;

                //  Handle show/hide toggle ourselves
                $('#map-tools-btn').on('click', function(evt) {
                    self.toggleMapTools();
                    return false;
                });
                $('#map-tools-dropdown').on('click', 'a', function(evt) {
                    if($(evt.target).attr('name') === 'map-tools'){
                        self.togglefilter(evt);
                    }
                    return false;
                });

                //  suppress default bahavior of the bootstrap menu to auto close
                $('#map-tools-btn').on('hide.bs.dropdown', false);            
                $('#map-tools-btn').on('show.bs.dropdown', false);


                this.expanded = ko.observable(false);
                this.expanded.subscribe(function(status){
                    this.toggleFilterSection($('#map-filter'), status);
                }, this);

                this.query = {
                    filter: {
                        geometry:{
                            type: ko.observable(''),
                            coordinates: ko.observable([])
                        },
                        buffer: {
                            width: ko.observable('0'),
                            unit: ko.observable('ft')
                        },
                        inverted: ko.observable(false)
                    },
                    changed: ko.pureComputed(function(){
                        return (ko.toJSON(this.query.filter.geometry.coordinates()) + 
                            ko.toJSON(this.query.filter.buffer.width()) + 
                            ko.toJSON(this.query.filter.inverted()));
                    }, this).extend({ rateLimit: 200 })
                }

                ko.applyBindings(this.query.filter, $('#map-tools-dropdown')[0]); 

                this.query.filter.buffer.width.subscribe(function(){
                    self.applyBuffer();
                });

                this.query.filter.geometry.type.subscribe(function(type){
                    var enabled = type !== '';
                    this.trigger('enabled', enabled, this.query.filter.inverted());
                    return enabled;
                }, this);


                this.vectorLayer = new ResourceLayerModel({}, function(features){
                    self.resourceFeatures = features;
                    
                    //wrap feature as a backbone model and add all to a collection, for efficient retrieval by id.
                    var featureModels = _.map(features, function (f) {
                        return {
                            id: f.id,
                            feature: f
                        };
                    });
                    self.resourceFeaturesCollection = new Backbone.Collection(featureModels);
                    if (self.highlightOnLoad) {
                        _.defer(function () { self.highlightFeatures(self.highlightOnLoad.resultsarray, self.highlightOnLoad.entityIdArray) });
                    }
                    self.trigger('vectorlayerloaded', features);
                    if (!self.cancelFitBaseLayer){
//                         setTimeout(function() {
//                               self.zoomToExtent(self.vectorLayer.getSource().getExtent());
//                         }, 500);         
                    }
                }).layer();
                this.map = new MapView({
                    el: $('#map'),
                    overlays: [this.vectorLayer]
                });


                this.bufferFeatureOverlay = new ol.layer.Vector({
                    source: new ol.source.Vector({
                        features: new ol.Collection()
                    }),
                    style: new ol.style.Style({
                        fill: new ol.style.Fill({
                            color: 'rgba(123, 123, 255, 0.5)'
                        }),
                        stroke: new ol.style.Stroke({
                            color: '#ff6633',
                            width: 2,
                            lineDash: [4,4]
                        })
                    })
                }); 
                this.bufferFeatureOverlay.setMap(this.map.map);
                this.FeatureOverlayCollection = new ol.Collection();                   
                var style = function (feature) {
                    return [new ol.style.Style({
                        fill: new ol.style.Fill({
                            color: 'rgba(92, 184, 92, 0.2)'
                        }),
                        stroke: new ol.style.Stroke({
                            color: '#ffcc33',
                            width: 2
                        }),
                        image: new ol.style.Circle({
                            radius: 7,
                            fill: new ol.style.Fill({
                                color: 'rgba(92, 184, 92, 0.2)'
                            }),
                            stroke: new ol.style.Stroke({
                                color: '#ffcc33',
                                width: 2
                            })
                        })
                    })];
                }
                this.drawingFeatureOverlay = new ol.layer.Vector({
                    source: new ol.source.Vector({
                        features: this.FeatureOverlayCollection
                    }),
                    style: style
                });
                this.drawingFeatureOverlay.setMap(this.map.map);
                
                ko.applyBindings(this.map, $('#basemaps-panel')[0]);

                var hideAllPanels = function(){
                    $("#basemaps-panel").addClass("hidden");

                    //Update state of remaining buttons
                    $("#inventory-basemaps")
                        .removeClass("arches-map-tools-pressed")
                        .addClass("arches-map-tools")
                        .css("border-bottom-left-radius", "1px");
                };

                //Inventory-basemaps button opens basemap panel
                $("#inventory-basemaps").click(function (){
                    if ($(this).hasClass('arches-map-tools-pressed')) {
                        hideAllPanels();
                    } else {
                        $("#basemaps-panel").removeClass("hidden");

                        //Update state of current button and adjust position
                        $("#inventory-basemaps")
                            .addClass("arches-map-tools-pressed")
                            .removeClass("arches-map-tools")
                            .css("border-bottom-left-radius", "5px");
                    }
                });

                $(".basemap").click(function (){ 
                    var basemap = $(this).attr('id');
                    _.each(self.map.baseLayers, function(baseLayer){ 
                        baseLayer.layer.setVisible(baseLayer.id == basemap);
                    });
                    hideAllPanels();
                });

                //Close Button
                $(".close").click(function (){ 
                    hideAllPanels();
                });

                
                var mouseoverFeatureTooltip = $('#feature_tooltip');
                var currentMousePx = null;
                var archesFeaturesCache = {};

                var showMouseoverFeatureTooltip = function(feature) {
                    var mapheight = self.map.$el.height();
                    var mapwidth = self.map.$el.width();
                    if (currentMousePx) {
                        mouseoverFeatureTooltip.find('#tooltip-text').html(feature.get('primaryname'));
                        if(currentMousePx[0] < mapwidth*0.33){
                            mouseoverFeatureTooltip.removeClass('left')
                                .addClass('right');
                        }
                        if(currentMousePx[0] > mapwidth*0.66){
                            mouseoverFeatureTooltip.removeClass('right')
                                .addClass('left');
                        }
                        if(mouseoverFeatureTooltip.hasClass('left')){
                            mouseoverFeatureTooltip.css({
                                left: (currentMousePx[0] - mouseoverFeatureTooltip.width()+20) + 'px',
                                top: (currentMousePx[1] - mouseoverFeatureTooltip.height()/2) + 'px'
                            });
                        }
                        if(mouseoverFeatureTooltip.hasClass('right')){
                            mouseoverFeatureTooltip.css({
                                left: (currentMousePx[0] + 45) + 'px',
                                top: (currentMousePx[1] - mouseoverFeatureTooltip.height()/2) + 'px'
                            });
                        }
                        mouseoverFeatureTooltip.show();
                    }
                };

                self.map.on('mousePositionChanged', function (mousePosition, pixels, feature) {
                    var cursorStyle = "";
                    currentMousePx = pixels;

                    if (feature && (feature.get('arches_marker') || feature.get('arches_cluster'))) {
                        cursorStyle = "pointer";
                        if (feature.get('arches_marker') || feature.get('point_count') === 1) {
                            if (feature.get('features')) {
                                feature = feature.get('features')[0];
                            }
                            var fullFeature = archesFeaturesCache[feature.getId()];
                            if (fullFeature && fullFeature != 'loading') {
                                showMouseoverFeatureTooltip(fullFeature);
                            } else if (fullFeature != 'loading') {
                                archesFeaturesCache[feature.getId()] = 'loading';
                                $.ajax({
                                    url: arches.urls.map_markers + 'all?entityid=' + feature.getId(),
                                    success: function(response) {
                                        fullFeature = geoJSON.readFeature(response.features[0]);
                                        var geom = fullFeature.getGeometry();
                                        geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));

                                        fullFeature.set('select_feature', true);
                                        fullFeature.set('entityid', fullFeature.getId());

                                        archesFeaturesCache[feature.getId()] = fullFeature;
                                        showMouseoverFeatureTooltip(fullFeature);
                                    }
                                });
                            }
                        }
                    } else {
                        mouseoverFeatureTooltip.hide();
                    }
                    self.map.$el.css("cursor", cursorStyle);
                });

                var clusterFeaturesCache = {};

                var selectFeatureOverlay = new ol.layer.Vector({
                    source: new ol.source.Vector({
                        features: new ol.Collection()
                    }),                    
                    style: function(feature, resolution) {
                        var isSelectFeature = _.contains(feature.getKeys(), 'select_feature');
                        var fillOpacity = isSelectFeature ? 0.3 : 0;
                        var strokeOpacity = isSelectFeature ? 0.9 : 0;
                        return [new ol.style.Style({
                            fill: new ol.style.Fill({
                                color: 'rgba(0, 255, 255, ' + fillOpacity + ')'
                            }),
                            stroke: new ol.style.Stroke({
                                color: 'rgba(0, 255, 255, ' + strokeOpacity + ')',
                                width: 3
                            }),
                            image: new ol.style.Circle({
                                radius: 10,
                                fill: new ol.style.Fill({
                                    color: 'rgba(0, 255, 255, ' + fillOpacity + ')'
                                }),
                                stroke: new ol.style.Stroke({
                                    color: 'rgba(0, 255, 255, ' + strokeOpacity + ')',
                                    width: 3
                                })
                            })
                        })];
                    }
                });
                selectFeatureOverlay.setMap(self.map.map);
                
                $('.resource-info-closer').click(function() {
                    $('#resource-info').hide();
                    selectFeatureOverlay.getSource().clear();
                    $('.resource-info-closer')[0].blur();
                });

                $('.cluster-info-closer').click(function() {
                    $('#cluster-info').hide();
                    $('.cluster-info-closer')[0].blur();
                });

                this.viewModel = {
                    selectedResource: ko.observable({}),
                    clusterFeatures: ko.observableArray()
                };
                ko.applyBindings(this.viewModel, $('#resource-info')[0]);
                ko.applyBindings(this.viewModel, $('#cluster-info')[0]);

                var showFeaturePopup = function(feature) {
                    var resourceData = {
                        id: feature.getId(),
                        reportLink: arches.urls.reports + feature.getId()
                    };
                    var typeInfo = resourceTypes[feature.get('entitytypeid')];
                    $('#cluster-info').hide();
                    if (typeInfo) {
                        resourceData.typeName = resourceTypes[feature.get('entitytypeid')].name;
                        resourceData.typeIcon = resourceTypes[feature.get('entitytypeid')].icon;
                    }
                    _.each(feature.getKeys(), function (key) {
                        resourceData[key] = feature.get(key);
                    });
                    
                    selectFeatureOverlay.getSource().clear();
                    selectFeatureOverlay.getSource().addFeature(feature);
                    self.viewModel.selectedResource(resourceData);
                    $('#resource-info').show();
                };

                this.showFeaturePopup = showFeaturePopup;

                var showClusterPopup = function(feature) {
                    var ids = [];
                    _.each(feature.get('features'), function(childFeature) {
                        ids.push(childFeature.getId());
                    });
                    var featureIds = ids.join(',');
                    var completeFeatures = clusterFeaturesCache[featureIds];

                    self.viewModel.clusterFeatures.removeAll();
                    $('#resource-info').hide();
                    $('#cluster-info').show();

                    if (completeFeatures) {
                        self.viewModel.clusterFeatures.push.apply(self.viewModel.clusterFeatures, completeFeatures);
                    } else {
                        $.ajax({
                            url: arches.urls.map_markers + 'all?entityid=' + featureIds,
                            success: function(response) {
                                clusterFeaturesCache[featureIds] = response.features;
                                self.viewModel.clusterFeatures.push.apply(self.viewModel.clusterFeatures, response.features);
                            }
                        });
                    }
                };

                var currentZoom;
                this.map.on('viewChanged', function (zoom, extent) {
                    currentZoom = zoom;
                });

                this.map.on('mapClicked', function(e, clickFeature) {
                    selectFeatureOverlay.getSource().clear();
                    $('#resource-info').hide();
                    if (clickFeature) {
                        var keys = clickFeature.getKeys();
                        var isCluster = _.contains(keys, "features") || _.contains(keys, "point_count");
                        var isArchesFeature = (_.contains(keys, 'arches_cluster') || _.contains(keys, 'arches_marker'));
                        var numFeatures = 0;
                        if(isCluster) {
                            if(clickFeature.get('features')) {
                                numFeatures = clickFeature.get('features').length;
                            } else if (clickFeature.get('point_count')) {
                                numFeatures = clickFeature.get('point_count');
                            }
                        }
                        if (isCluster && numFeatures > 1) {                        
                            if (currentZoom !== arches.mapDefaults.maxZoom) {
                                var extent = clickFeature.getGeometry().getExtent();
                                if(clickFeature.get("features")) {
                                    //an ol cluster - we have information about the sub-features, so zoom to their extents
                                    _.each(clickFeature.get("features"), function (feature) {
                                        if (_.contains(keys, 'extent')) {
                                            featureExtent = ol.extent.applyTransform(feature.get('extent'), ol.proj.getTransform('EPSG:4326', 'EPSG:3857'));
                                        } else {
                                            featureExtent = feature.getGeometry().getExtent();
                                        }
                                        extent = ol.extent.extend(extent, featureExtent);
                                    });
                                    self.map.map.getView().fit(extent, (self.map.map.getSize()));
                                } else {
                                    //a supercluster cluster. We only know the number of points and their shared centre;
                                    // Zoom in by two levels, and centre the map on this point
                                    var view = self.map.map.getView();
                                    
                                    //get desired new zoom
                                    var clusterId = clickFeature.get("cluster_id");
                                    var zoom = Math.ceil(view.getZoom());
                                    
                                    var newZoom = zoom + 2;
                                    if(clusterId) {
                                        var clustertype = clickFeature.get('type');
                                        if(clustertype === 'result') {
                                            newZoom = this.resultsIndex.getClusterExpansionZoom(clusterId, zoom);
                                        } else if(clustertype === 'nonresult') {
                                            newZoom = this.nonResultsIndex.getClusterExpansionZoom(clusterId, zoom); 
                                        }
                                    }
                                    view.setZoom(newZoom + 1);
                                    view.setCenter(clickFeature.getGeometry().getCoordinates());
                                }
                            } else {
                                showClusterPopup(clickFeature);
                            }
                        } else {
                            if (isCluster) {
                                //cluster of 1
                                clickFeature = clickFeature.get('features')[0];
                                keys = clickFeature.getKeys();
                            }
                            if (!_.contains(keys, 'select_feature')) {
                                //individual feature
                                if (isArchesFeature) {
                                    if (archesFeaturesCache[clickFeature.getId()] && archesFeaturesCache[clickFeature.getId()] !== 'loading'){
                                        showFeaturePopup(archesFeaturesCache[clickFeature.getId()]);
                                    } else {
                                        $('.map-loading').show();
                                        archesFeaturesCache[clickFeature.getId()] = 'loading';
                                        $.ajax({
                                            url: arches.urls.map_markers + 'all?entityid=' + clickFeature.getId(),
                                            success: function(response) {
                                                var feature = geoJSON.readFeature(response.features[0]);
                                                var geom = feature.getGeometry();
                                                geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));

                                                feature.set('select_feature', true);
                                                feature.set('entityid', feature.getId());

                                                archesFeaturesCache[clickFeature.getId()] = feature;
                                                $('.map-loading').hide();
                                                showFeaturePopup(feature);
                                            }
                                        });
                                    }
                                }
                            }
                        }
                    }
                }.bind(this));

                this.resultLayer = new ResourceLayerModel({entitytypeid: null, vectorColor: arches.resourceMarker.defaultColor}).layer();
                this.map.map.addLayer(this.resultLayer);
                var styleFactory = function (color, zIndex) {
                    var rgb = utils.hexToRgb(color);
                    return [new ol.style.Style({
                        text: new ol.style.Text({
                            text: arches.resourceMarker.icon,
                            font: 'normal 42px ' + arches.resourceMarker.font,
                            offsetX: 5,
                            offsetY: ((42/2)*-1)-5,
                            fill: new ol.style.Fill({
                                color: 'rgba(126,126,126,0.3)',
                            })
                        }),
                        zIndex: zIndex
                    }), new ol.style.Style({
                        text: new ol.style.Text({
                            text: arches.resourceMarker.icon,
                            font: 'normal 42px ' + arches.resourceMarker.font,
                            offsetY: (42/2)*-1,
                            stroke: new ol.style.Stroke({
                                color: 'white',
                                width: 3
                            }),
                            fill: new ol.style.Fill({
                                color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.9)',
                            })
                        }),
                        zIndex: zIndex
                    })];
                };
                var normalStyle = styleFactory(arches.resourceMarker.defaultColor, 1000000);
                var highlightStyle = styleFactory('#4CAE4C', 9999999);

                this.currentPageLayer = new ol.layer.Vector({
                    source: new ol.source.Vector({
                        format: new ol.format.GeoJSON()
                    }),
                    style: function(feature) {
                        if(feature.get('highlight')) {
                            return highlightStyle;
                        } else {
                            return normalStyle;
                        }
                    }
                });
                this.map.map.addLayer(this.currentPageLayer);
            },

            zoomToResource: function(resourceid){
                this.cancelFitBaseLayer = true;
                var feature = this.resultLayer.vectorSource.getFeatureById(resourceid);
                if(feature.getGeometry().getGeometries().length > 1){
                    var extent = feature.getGeometry().getExtent();
                    var minX = extent[0];
                    var minY = extent[1];
                    var maxX = extent[2];
                    var maxY = extent[3];
                    var polygon = new ol.geom.Polygon([[[minX, minY], [maxX, minY], [maxX, maxY], [minX, maxY], [minX, minY]]]);
                    //polygon.transform('EPSG:3857', 'EPSG:4326');
                    this.map.map.getView().fit(polygon, this.map.map.getSize(), {maxZoom:16}); 
                }else{
                    this.map.map.getView().fit(feature.getGeometry().getGeometries()[0], this.map.map.getSize(), {maxZoom:16});                    
                }
            },
            
            zoomToExtent: function(extent){
                var size = this.map.map.getSize();
                var view = this.map.map.getView();
                view.fit(
                    extent,
                    size
                );
            },

            highlightFeatures: function(resultsarray, entityIdArray){
                var sameResultSet = (entityIdArray[0] === '_none');

                if (this.resourceFeatures) {
                    if (entityIdArray[0] === '_all') {
                        this.allResultsPoints = _.clone(this.resourceFeatures);
                        if(SHOW_NON_RESULT_MARKERS) {
                            this.allNonResultsPoints = [];
                        }
                    } else {
                        if(sameResultSet) {
                            //new page of existing results 
                        } else {
                            //brand new result set
                            
                            // get all features which are in the result set
                            this.allResultsPoints = []
                            _.each(entityIdArray, function (id) {
                                var result = this.resourceFeaturesCollection.get(id);
                                if(result) {
                                    this.allResultsPoints.push(result.get('feature'));
                                }
                                
                            }.bind(this));

                            if(SHOW_NON_RESULT_MARKERS) {
                                // get the features not in the result set
                                var resourceFeaturesCollectionCopy = this.resourceFeaturesCollection.clone();
                                resourceFeaturesCollectionCopy.remove(entityIdArray)
                                this.allNonResultsPoints = resourceFeaturesCollectionCopy.map(function (f) {
                                    return f.get('feature');
                                });
                            }
                        }
                    }

                    var currentPageIDs = _.map(resultsarray.results.hits.hits, function (hit) {
                        return hit['_id'];
                    });
                    var partitionedPoints = _.partition(this.allResultsPoints, function (point) {
                        return currentPageIDs.indexOf(point.id) > -1;
                    });
                    
                    this.currentPageResults = partitionedPoints[0];
                    this.notCurrentPageResults = partitionedPoints[1];

                    //fill cluster index with all results not on the current page
                    this.resultsIndex = supercluster({
                        radius: 100 ,
                        maxZoom: 16
                    });
                    this.resultsIndex.load(this.notCurrentPageResults);
                    
                    if(SHOW_NON_RESULT_MARKERS) {
                        this.nonResultsIndex = supercluster({
                            radius: 100,
                            maxZoom: 16
                        });
                        this.nonResultsIndex.load(this.allNonResultsPoints);
                    }
                    
                    //plot current page results
                    this.currentPageLayer.getSource().clear();
                    
                    var convertToOlFeatures = function (geoJsonFeatures) {
                        var olFeatures = [];
                        _.each(geoJsonFeatures, function (geoJsonFeature) {
                            //project to map coordinates
                            var coords = ol.proj.transform(geoJsonFeature.geometry.coordinates, 'EPSG:4326', 'EPSG:3857');
                            var f = new ol.Feature(new ol.geom.Point(
                                coords
                            ));
                            f.setProperties({arches_marker: true});
                            f.setId(geoJsonFeature.id);
                            olFeatures.push(f);
                        });
                        return olFeatures;
                    }
                    
                    var currentPageOlFeatures = convertToOlFeatures(this.currentPageResults);
                    
                    this.currentPageLayer.getSource().addFeatures(currentPageOlFeatures);

                    if (this.drawingFeatureOverlay.getSource().getFeatures().length === 0 && this.query.filter.geometry.type() !== 'bbox') {
                        this.zoomToResults();
                    }
                    
                    this.onViewChanged();
                    $('.spinner').hide();
                } else {
                    this.highlightOnLoad = {
                        resultsarray: resultsarray,
                        entityIdArray: entityIdArray
                    };
                }
            },
            
            onViewChanged: function () {
                // return;
                var extentOl = this.map.map.getView().calculateExtent(this.map.map.getSize());
                var extentLatLng = ol.proj.transformExtent(extentOl, 'EPSG:3857', 'EPSG:4326');
                
                var zoom = Math.ceil(this.getMapZoom());
                
                if(!zoom) { return; }
                
                var superClusterToOlFeature = function (cluster, properties) {
                    //project to map coordinates
                    var coords = ol.proj.transform(cluster.geometry.coordinates, 'EPSG:4326', 'EPSG:3857');
                    var f = new ol.Feature(new ol.geom.Point(
                        coords
                    ));
                    f.setProperties( _.extend({}, cluster.properties, properties) );
                    if(cluster.id) {
                        f.setId(cluster.id);
                    }
                    return f;
                }
                
                if(this.resultsIndex) {
                    
                    //clear the clusters layer
                    var resultsClustersSource = this.resultLayer.getSource()
                    resultsClustersSource.clear();
                    
                    var resultsClusters = this.resultsIndex.getClusters(extentLatLng, zoom);
                    
                    //convert supercluster GeoJSON features to ol features
                    var resultsClusterFeatures = _.map(resultsClusters, function (c) {
                        return superClusterToOlFeature(c, {type: 'result'});
                    });
                    
                    resultsClustersSource.addFeatures(resultsClusterFeatures);
                }
                
                if(SHOW_NON_RESULT_MARKERS && this.nonResultsIndex) {
                    var nonResultsClustersSource = this.vectorLayer.getSource()
                    nonResultsClustersSource.clear();
                    
                    var nonResultsClusters = this.nonResultsIndex.getClusters(extentLatLng, zoom);
                    var nonResultsClustersFeatures = _.map(nonResultsClusters, function (c) {
                        return superClusterToOlFeature(c, {type: 'nonresult'});
                    });
                    
                    nonResultsClustersSource.addFeatures(nonResultsClustersFeatures);
                }
                
            },

            zoomToResults: function () {
                var allResultsGeoJSON = {
                    type: "FeatureCollection",
                    features: this.allResultsPoints
                }
                var extent = this.getResultExtents();
                if(extent) {
                    var extentProjected = ol.proj.transformExtent(extent, 'EPSG:4326', 'EPSG:3857');
                    this.map.map.getView().fit(extentProjected, this.map.map.getSize());
                }
            },

            getResultExtents: function () {
                var extent = null
                _.each(this.allResultsPoints, function (point) {
                    var latlon = point.geometry.coordinates;
                    if(!extent) {
                         extent = {
                             w: latlon[0],
                             n: latlon[1],
                             e: latlon[0],
                             s: latlon[1]
                         };
                     } else {
                         if(latlon[0] < extent.w) {
                             extent.w = latlon[0];
                         } else if(latlon[0] > extent.e) {
                             extent.e = latlon[0];
                         }
                         
                         if(latlon[1] > extent.n) {
                             extent.y = latlon[1];
                         } else if(latlon[1] < extent.s) {
                             extent.s = latlon[1];
                         }
                     }
                });
                
                return extent ? [extent.w, extent.s, extent.e, extent.n]: null;
            },

            selectFeatureById: function(resourceid){
                this.unselectAllFeatures();
                var feature = this.currentPageLayer.getSource().getFeatureById(resourceid);
                if(feature){
                    feature.set('highlight', true);
                    return feature;
                } 
            },

            unselectAllFeatures: function(){
                this.currentPageLayer.getSource().forEachFeature(function(feature) {
                    feature.set('highlight', false);
                });
            },

            getMapExtent: function(){
                var extent = ol.proj.transformExtent(this.map.map.getView().calculateExtent(this.map.map.getSize()), 'EPSG:3857', 'EPSG:4326');
                return extent;
            },
            
            getMapZoom: function () {
                return this.map.map.getView().getZoom();
            },

            onMoveEnd: function(evt) {
                this.query.filter.geometry.coordinates(this.getMapExtent());
            },

            togglefilter: function(evt){
                var link = $(evt.target).closest('a');
                var data = link.data();
                var item = link.find('i');
 
                if (!(item.hasClass("fa-check"))){
                    this.enableFilter(data.tooltype);
                }else{
                    this.clear();
                }
            },

            enableFilter: function(tooltype){
                if(tooltype){
                    if(tooltype === 'map-extent'){
                        this.removeDrawingTools();
                        this.clearDrawingFeatures();
                        this.query.filter.geometry.type('bbox');
                        this.query.filter.geometry.coordinates(this.getMapExtent());
                        this.map.map.on('moveend', this.onMoveEnd, this);
                    }else{
                        this.clearDrawingFeatures();
                        this.query.filter.geometry.type(tooltype);
                        this.changeDrawingTool(this.map.map, tooltype);
                        this.map.map.un('moveend', this.onMoveEnd, this);     
                    }                  
                }
            },

            changeDrawingTool: function(map, tooltype){
                this.disableDrawingTools();
                var modifyTool = new ol.interaction.Modify({
                    features: this.FeatureOverlayCollection,
                    // the SHIFT key must be pressed to delete vertices, so
                    // that new vertices can be drawn at the same position
                    // of existing vertices
                    deleteCondition: function(event) {
                        return ol.events.condition.shiftKeyOnly(event) &&
                        ol.events.condition.singleClick(event);
                    }
                });
                map.addInteraction(modifyTool);
                this.drawingtool = new ol.interaction.Draw({
                    features: this.FeatureOverlayCollection,
                    type: tooltype
                });
                this.drawingtool.set('type', tooltype);

                this.drawingtool.on('drawstart', function(){
                    if(this.drawingtool.get('type') !== 'Point'){
                        this.clearDrawingFeatures();                       
                    }
                }, this);

                this.drawingtool.on('drawend', function(evt){
                    var self = this;
                    var geometry = evt.feature.getGeometry().clone();
                    geometry.transform('EPSG:3857', 'EPSG:4326');
                    this.query.filter.geometry.coordinates(geometry.getCoordinates());

                    //this.applyBuffer();
                    
                    evt.feature.on('change', function(evt) {
                        var geometry = evt.target.getGeometry().clone();
                        geometry.transform('EPSG:3857', 'EPSG:4326');
                        self.query.filter.geometry.coordinates(geometry.getCoordinates());
                        //self.applyBuffer();
                    });
                }, this);

                this.enableDrawingTools();
            },

            enableDrawingTools: function(){
                if(this.drawingtool){
                    this.map.map.addInteraction(this.drawingtool);
                }
            },

            disableDrawingTools: function(){
                if(this.drawingtool){
                    this.map.map.removeInteraction(this.drawingtool);
                }
            },

            removeDrawingTools: function(){
                this.disableDrawingTools();
                delete this.drawingtool;
            },

            clearDrawingFeatures: function(){
                if (this.bufferFeatureOverlay){
                    this.bufferFeatureOverlay.getSource().clear();                 
                }
                if (this.drawingFeatureOverlay){
                    this.drawingFeatureOverlay.getSource().clear();
                }
            },

            applyBuffer: function(){
                var self = this;
                var params = {
                    filter: ko.toJSON(this.query.filter)
                }; 
                if(this.query.filter.buffer.width() > 0 && this.drawingFeatureOverlay.getSource().getFeatures().length > 0){
                    $.ajax({
                        type: "GET",
                        url: arches.urls.buffer,
                        data: {
                            filter: ko.toJSON(this.query.filter)
                        },
                        success: function(results){
                            var source = new ol.source.Vector({
                                features: (new ol.format.GeoJSON()).readFeatures({
                                    type: 'FeatureCollection', 
                                    features: [{
                                        type:'Feature',
                                        geometry: JSON.parse(results)}]
                                })
                            });
                            var feature = source.getFeatures()[0];
                            
                            feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
                            self.bufferFeatureOverlay.getSource().clear();  
                            self.bufferFeatureOverlay.getSource().addFeature(feature);
                        },
                        error: function(){}
                    });                    
                }else{
                    this.bufferFeatureOverlay.getSource().clear();  
                }
            },

            toggleMapTools: function() {
                if($('#map-tools-btn').hasClass('open')){
                    this.disableDrawingTools();
                }
                else {
                    this.enableDrawingTools();
                }
                $('#map-tools-btn').toggleClass('open');
            },

            toggleFilterSection: function(ele, expand){
                if(expand){
                    this.slideToggle(ele, 'show');
                }else{
                    this.slideToggle(ele, 'hide');               
                }
            },

            slideToggle: function(ele, showOrHide){
                var self = this;
                if ($(ele).is(":visible") && showOrHide === 'hide'){
                    ele.slideToggle('slow');
                    return;
                }

                if (!($(ele).is(":visible")) && showOrHide === 'show'){
                    ele.slideToggle('slow', function(){
                        self.map.map.updateSize();
                        self.zoomToResults();
                    });
                    return;
                }

                if (!showOrHide){
                    ele.slideToggle('slow');                    
                }
            },

            restoreState: function(filter, expanded){
                this.map.map.once('change:size', function(){
                    if(typeof filter !== 'undefined' && 'geometry' in filter && filter.geometry.coordinates.length > 0){
                        this.query.filter.inverted(ko.utils.unwrapObservable(filter.inverted));                        
                        this.query.filter.geometry.type(ko.utils.unwrapObservable(filter.geometry.type));
                        this.query.filter.geometry.coordinates(ko.utils.unwrapObservable(filter.geometry.coordinates));
                        this.query.filter.buffer.width(ko.utils.unwrapObservable(filter.buffer.width));
                        this.query.filter.buffer.unit(ko.utils.unwrapObservable(filter.buffer.unit));

                        var coordinates = this.query.filter.geometry.coordinates();
                        var type = this.query.filter.geometry.type();
                        if(type === 'bbox'){
                            this.map.map.on('moveend', this.onMoveEnd, this); 

                            var extent = ol.proj.transformExtent(coordinates, 'EPSG:4326', 'EPSG:3857');
                            this.zoomToExtent(extent);

                        }else{
                            var feature = new ol.Feature({
                                geometry: new ol.geom[type](coordinates)
                            });

                            feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
                            this.zoomToExtent(feature.getGeometry().getExtent());
                            this.drawingFeatureOverlay.getSource().addFeature(feature);
                            this.changeDrawingTool(this.map.map, type);
                            this.disableDrawingTools();

                            feature.on('change', function(evt) {
                                var geometry = evt.target.getGeometry().clone();
                                geometry.transform('EPSG:3857', 'EPSG:4326');
                                this.query.filter.geometry.coordinates(geometry.getCoordinates());
                                //self.applyBuffer();
                            }, this);
                        }
                    }

                }, this);

                if(typeof expanded === 'undefined'){
                    expanded = false;
                }
                this.expanded(expanded);

            },

            clear: function(){
                this.removeDrawingTools();
                this.clearDrawingFeatures();
                this.query.filter.inverted(false);
                this.query.filter.geometry.type('');
                this.query.filter.geometry.coordinates([]);
                this.map.map.un('moveend', this.onMoveEnd, this);
            },

            clusterItemClick: function (e) {
                var entityid = $(e.target).closest('.cluster-item-link').data().entityid;
                var geoJSONFeature = ko.utils.arrayFirst(this.viewModel.clusterFeatures(), function(item) {
                    return entityid === item.id;
                });

                var feature = geoJSON.readFeature(geoJSONFeature);
                var geom = feature.getGeometry();
                geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));

                feature.set('select_feature', true);
                feature.set('entityid', feature.getId());

                this.showFeaturePopup(feature);
            }

        });
});