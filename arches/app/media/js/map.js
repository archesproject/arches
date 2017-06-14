require([
    'jquery',
    'underscore',
    'backbone',
    'openlayers',
    'knockout',
    'arches',
    'resource-layer-info',
    'views/map',
    'map/layers',
    'map/resource-layers',
    'map/layer-model',
    'selected-resource-id',
    'resource-types',
    'bootstrap',
    'select2',
    'plugins/jquery.knob.min'
], function($, _, Backbone, ol, ko, arches, layerInfo, MapView, layers, resourceLayers, LayerModel, selectedResourceId, resourceTypes) {
    var geoJSON = new ol.format.GeoJSON();
    var PageView = Backbone.View.extend({
        el: $('body'),
        events: {
            'click .visibility-toggle': 'visibilityToggle',
            'click .on-map-toggle': 'onMapToggle',
            'click .layer-zoom': 'layerZoom',
            'click .cluster-item-link': 'clusterItemClick',
            'change:resolution': 'ZoomChange'
        },
        initialize: function(options) {
            var self = this;
            var mapLayers = [];
            var elevateArchesResourceLayers = function () {
                map.map.getLayers().forEach(function(layer, index) {
                    if (layer.get('is_arches_layer')) {
                        map.map.removeLayer(layer);
                        map.map.addLayer(layer);
                    }
                });
            };
            _.each(layers, function(layer, index) {
                if (layer.onMap) {
                    if (typeof layer.layer == 'function') {
                        layer.layer = layer.layer();
                    }
                    mapLayers.push(layer.layer);
                }
                layer.onMap = ko.observable(layer.onMap);
                layers[index].onMap.subscribe(function(add) {
                    // allow for lazy instantiation (and thus load)
                    if (typeof layer.layer == 'function') {
                        layer.layer = layer.layer();
                    }
                    if (add) {
                        map.map.addLayer(layer.layer);
                        elevateArchesResourceLayers();
                    } else {
                        map.map.removeLayer(layer.layer);
                    }
                });
                layer.active = ko.observable(true);
                layers[index].active.subscribe(function(show) {
                    layer.layer.setVisible(show);
                });
                layer.filtered = ko.observable(false);
            });
            var map = new MapView({
                el: $('#map'),
                overlays: mapLayers.reverse()
            });

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
            selectFeatureOverlay.setMap(map.map);

            self.viewModel = {
                baseLayers: map.baseLayers,
                layers: ko.observableArray(layers),
                filterTerms: ko.observableArray(),
                zoom: ko.observable(arches.mapDefaults.zoom),
                mousePosition: ko.observable(''),
                selectedResource: ko.observable({}),
                selectedAddress: ko.observable(''),
                clusterFeatures: ko.observableArray()
            };
            self.map = map;
            var clusterFeaturesCache = {};
            var archesFeaturesCache = {};

            var selectDeafultFeature = function (features) {
                var feature = _.find(features, function (feature) {
                    return feature.getId() === selectedResourceId;
                });
                if (feature) {
                    var geom = geoJSON.readGeometry(feature.get('geometry_collection'));
                    geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
                    map.map.getView().fit(geom.getExtent(), map.map.getSize());
                    selectFeatureOverlay.getSource().clear();
                    selectFeatureOverlay.getSource().addFeature(feature);
                    selectedResourceId = null;
                }
            };
            if (selectedResourceId) {
                selectDeafultFeature(resourceLayers.features());

                resourceLayers.features.subscribe(function (features) {
                    selectDeafultFeature(features);
                });
            }

            self.viewModel.filterTerms.subscribe(function () {
                var terms = self.viewModel.filterTerms()
                _.each(self.viewModel.layers(), function(layer) {
                    var filtered = true;
                    if (terms.length == 0) {
                        filtered = false;
                    } else {
                        _.each(terms, function(term) {
                            if (term.text === layer.name) {
                                filtered = false;
                            } else if (_.contains(layer.categories, term.text)) {
                                filtered = false;
                            }
                        });
                    }
                    layer.filtered(filtered)
                });
            });

            map.on('layerDropped', function (layer, name) {
                var layerModel = new LayerModel({
                      name: name,
                      description: '',
                      categories: [''],
                      icon: 'fa fa-map-marker',
                      layer: layer,
                      onMap:  ko.observable(true),
                      active: ko.observable(true),
                      filtered: ko.observable(false)
                });
                layerModel.onMap.subscribe(function(add) {
                    if (add) {
                        map.map.addLayer(layer);
                        elevateArchesResourceLayers();
                    } else {
                        map.map.removeLayer(layer);
                    }
                });
                layerModel.active.subscribe(function(show) {
                    layer.setVisible(show);
                });
                self.viewModel.layers.push(layerModel);
                $('.knob').knob({
                    change: function (value) {
                        var layerId = this.$.data().layerid;
                        var layer = ko.utils.arrayFirst(self.viewModel.layers(), function(item) {
                            return layerId === item.id;
                        });
                        layer.layer.setOpacity(value/100);
                    }
                });
                $(".knob").css("font-size", 11);
                $(".knob").css("font-weight", 200);
                $('[data-toggle="popover"]').popover();
            });

            map.on('viewChanged', function (zoom, extent) {
                
                _.each(map.overlays, function (layer) {
                    layer.setExtent(extent); //On zoom and panning, filter overlays by map extent.
                    
                });
                self.viewModel.zoom(zoom);
            });

            var mouseoverFeatureTooltip = $('#feature_tooltip');
            var currentMousePx = null;

            var showMouseoverFeatureTooltip = function(feature) {
                var mapheight = map.$el.height();
                var mapwidth = map.$el.width();
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
                            left: (currentMousePx[0] - mouseoverFeatureTooltip.width() - 15) + 'px',
                            top: (currentMousePx[1] - mouseoverFeatureTooltip.height()/2 + map.$el.offset().top) + 'px'
                        });
                    }
                    if(mouseoverFeatureTooltip.hasClass('right')){
                        mouseoverFeatureTooltip.css({
                            left: (currentMousePx[0] + 10) + 'px',
                            top: (currentMousePx[1] - mouseoverFeatureTooltip.height()/2 + map.$el.offset().top) + 'px'
                        });
                    }
                    mouseoverFeatureTooltip.show();
                }
            };
            
            
            map.on('mousePositionChanged', function (mousePosition, pixels, feature) {
                var cursorStyle = "";
                currentMousePx = pixels;
                self.viewModel.mousePosition(mousePosition);

                if (feature && (feature.get('arches_marker') || feature.get('arches_cluster'))) {
                    cursorStyle = "pointer";
                    if (feature.get('arches_marker') || feature.get('features').length === 1) {
                        feature = feature.get('features')[0];
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
                map.$el.css("cursor", cursorStyle);
            });

            $('.resource-info-closer').click(function() {
                $('#resource-info').hide();
                selectFeatureOverlay.getSource().clear();
                $('.resource-info-closer')[0].blur();
            });

            $('.cluster-info-closer').click(function() {
                $('#cluster-info').hide();
                $('.cluster-info-closer')[0].blur();
            });

            var showFeaturePopup = function(feature) {
                var resourceData = {
                    id: feature.getId(),
                    reportLink: arches.urls.reports + feature.getId()
                };
                var typeInfo = layerInfo[feature.get('entitytypeid')];
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

            map.on('mapClicked', function(e, clickFeature) {
                selectFeatureOverlay.getSource().clear();
                $('#resource-info').hide();
                if (clickFeature) {
                    var keys = clickFeature.getKeys();
                    var isCluster = _.contains(keys, "features");
                    var isArchesFeature = (_.contains(keys, 'arches_cluster') || _.contains(keys, 'arches_marker'));
                    if (isCluster && clickFeature.get('features').length > 1) {
                        if (self.viewModel.zoom() !== arches.mapDefaults.maxZoom) {
                            var extent = clickFeature.getGeometry().getExtent();
                            _.each(clickFeature.get("features"), function (feature) {
                                if (_.contains(keys, 'extent')) {
                                    featureExtent = ol.extent.applyTransform(feature.get('extent'), ol.proj.getTransform('EPSG:4326', 'EPSG:3857'));
                                } else {
                                    featureExtent = feature.getGeometry().getExtent();
                                }
                                extent = ol.extent.extend(extent, featureExtent);
                            });
                            map.map.getView().fit(extent, (map.map.getSize()));
                        } else {
                            showClusterPopup(clickFeature);
                        }
                    } else {
                        if (isCluster) {
                            clickFeature = clickFeature.get('features')[0];
                            keys = clickFeature.getKeys();
                        }
                        if (!_.contains(keys, 'select_feature')) {
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
            });
            
            var hideAllPanels = function () {
                $("#overlay-panel").addClass("hidden");
                $("#basemaps-panel").addClass("hidden");

                //Update state of remaining buttons
                $("#inventory-basemaps").removeClass("arches-map-tools-pressed");
                $("#inventory-basemaps").addClass("arches-map-tools");
                $("#inventory-basemaps").css("border-bottom-left-radius", "1px");

                $("#inventory-overlays").removeClass("arches-map-tools-pressed");
                $("#inventory-overlays").addClass("arches-map-tools");
                $("#inventory-overlays").css("border-bottom-right-radius", "1px");
            };

            ko.applyBindings(self.viewModel, $('body')[0]);

            $(".basemap").click(function (){
                var basemap = $(this).attr('id');
                _.each(map.baseLayers, function(baseLayer){
                    baseLayer.layer.setVisible(baseLayer.id == basemap);
                });
                hideAllPanels();
            });

            //Inventory-basemaps button opens basemap panel
            $(".inventory-basemaps").click(function (){
                if ($(this).hasClass('arches-map-tools-pressed')) {
                    hideAllPanels();
                } else {
                    $("#overlay-panel").addClass("hidden");
                    $("#basemaps-panel").removeClass("hidden");

                    //Update state of remaining buttons
                    $("#inventory-overlays").removeClass("arches-map-tools-pressed");
                    $("#inventory-overlays").addClass("arches-map-tools");
                    $("#inventory-overlays").css("border-bottom-right-radius", "3px");

                    //Update state of current button and adjust position
                    $("#inventory-basemaps").addClass("arches-map-tools-pressed");
                    $("#inventory-basemaps").removeClass("arches-map-tools");
                    $("#inventory-basemaps").css("border-bottom-left-radius", "3px");
                }
            });


            //Inventory-overlayss button opens overlay panel
            $("#inventory-overlays").click(function (){
                if ($(this).hasClass('arches-map-tools-pressed')) {
                    hideAllPanels();
                } else {
                    $("#overlay-panel").removeClass("hidden");
                    $("#basemaps-panel").addClass("hidden");

                    //Update state of remaining buttons
                    $("#inventory-basemaps").removeClass("arches-map-tools-pressed");
                    $("#inventory-basemaps").addClass("arches-map-tools");

                    //Update state of current button and adjust position
                    $("#inventory-overlays").addClass("arches-map-tools-pressed");
                    $("#inventory-overlays").removeClass("arches-map-tools");
                }
            });

            //Close Button
            $(".close").click(function (){
                hideAllPanels();
            });

            //Show and hide Layer Library.  
            $("#add-layer").click(function(){
                $( ".map-space" ).slideToggle(600);
                $( "#layer-library" ).slideToggle(600);
            });

            $("#back-to-map").click(function(){
                $( ".map-space" ).slideToggle(600);
                $( "#layer-library" ).slideToggle(600);
            });

            $('.knob').knob({
                change: function (value) {
                    var layerId = this.$.data().layerid;
                    var layer = ko.utils.arrayFirst(self.viewModel.layers(), function(item) {
                        return layerId === item.id;
                    });
                    layer.layer.setOpacity(value/100);
                }
            });
            $(".knob").css("font-size", 11);
            $(".knob").css("font-weight", 200);

            $(".ol-zoom").css("top", "10px");
            $(".ol-zoom").css("z-index", "500");
            $(".ol-attribution").css("margin-bottom", "70px");

            //Select2 Simple Search initialize
            $('.layerfilter').select2({
                data: function() {
                    var terms = [];
                    _.each(layers, function (layer) {
                        terms = _.union(terms, layer.categories, [layer.name]);
                    });

                    return {
                        results: _.map(terms, function(term) {
                            return {
                                id: _.uniqueId('term'),
                                text: term
                            };
                        })
                    };
                },
                placeholder: "Filter Layer List",
                multiple: true,
                maximumSelectionSize: 5
            });

            //filter layer library
            $(".layerfilter").on("select2-selecting", function(e) {
                self.viewModel.filterTerms.push(e.object);
            });

            $(".layerfilter").on("select2-removed", function(e) {
                var term = ko.utils.arrayFirst(self.viewModel.filterTerms(), function(term) {
                    return term.id === e.val;
                });

                self.viewModel.filterTerms.remove(term);
            });

            //Select2 Simple Search initialize
            $('.geocodewidget').select2({
                ajax: {
                    url: "geocoder",
                    dataType: 'json',
                    quietMillis: 250,
                    data: function (term, page) {
                        return {
                            q: term
                        };
                    },
                    results: function (data, page) {
                        return { results: data.results };
                    },
                    cache: true
                },
                minimumInputLength: 4,
                multiple: true,
                maximumSelectionSize: 1
            });

            $('.geocodewidget').on("select2-selecting", function(e) {
                var geom = geoJSON.readGeometry(e.object.geometry);
                geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
                self.map.map.getView().fit(geom.getExtent(), self.map.map.getSize());
                self.viewModel.selectedAddress(e.object.text);
                overlay.setPosition(ol.extent.getCenter(geom.getExtent()));
                overlay.setPositioning('center-center');
                $('#popup').show();
            });

            $('.geocodewidget').on('select2-removing', function () {
                $('#popup').hide();
            });

            var overlay = new ol.Overlay({
              element: $('#popup')[0]
            });

            map.map.addOverlay(overlay);

            $('[data-toggle="popover"]').popover();
        },
        getLayerById: function(layerId) {
            return ko.utils.arrayFirst(this.viewModel.layers(), function(item) {
                return layerId === item.id;
            });
        },
        visibilityToggle: function (e) {
            var layer = this.getLayerById($(e.target).closest('.visibility-toggle').data().layerid);
            layer.active(!layer.active());
        },
        onMapToggle: function (e) {
            var layer = this.getLayerById($(e.target).closest('.on-map-toggle').data().layerid);
            layer.onMap(!layer.onMap());
        },
        layerZoom: function (e) {
            var layer = this.getLayerById($(e.target).closest('.layer-zoom').data().layerid).layer;
            if (layer.getLayers) {
                layer = layer.getLayers().getArray()[0];
            }
            if (layer.getSource) {
                this.map.map.getView().fit(layer.getSource().getExtent(), this.map.map.getSize());
            }
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
    new PageView();
});