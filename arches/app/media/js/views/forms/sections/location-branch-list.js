define([
    'jquery', 
    'backbone', 
    'knockout', 
    'knockout-mapping', 
    'underscore',
    'openlayers',
    'views/forms/sections/branch-list',
    'views/map'
], function ($, Backbone, ko, koMapping, _, ol, BranchList, MapView) {
    var wkt = new ol.format.WKT();
    return BranchList.extend({
        initialize: function(options) {
            var self = this;
            var map = new MapView({
                el: this.$el.find('.map')
            });

            var addFeature = function (feature, editing) {
                var branch = koMapping.fromJS({
                    'editing': ko.observable(editing), 
                    'nodes': ko.observableArray(self.defaults)
                });
                var geom = feature.getGeometry();
                if (editing) {
                    self.removeEditedBranch();
                }
                geom.transform(ol.proj.get('EPSG:3857'), ol.proj.get('EPSG:4326'));
                _.each(branch.nodes(), function(node) {
                    if (node.entitytypeid() === self.dataKey) {
                        node.value(wkt.writeGeometry(geom));
                    }
                });
                self.viewModel.branch_lists.push(branch);
                self.trigger('change', 'geometrychange', branch);
                self.trigger('geometrychange', feature, wkt.writeGeometry(geom));
            };

            var bulkAddFeatures = function (features) {
                _.each(features, function(feature, i) {
                    addFeature(feature, i===features.length-1);
                });
                zoomToFeatureOverlay();
            };

            map.map.on('click', function(e) {
                map.map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                    if (_.contains(feature.getKeys(), 'branch')) {
                        self.removeEditedBranch();
                        feature.get('branch').editing(true);            
                    }
                });
            });

            map.on('layerDropped', function (layer) {
                var features = layer.getSource().getFeatures();

                bulkAddFeatures(features);

                map.map.removeLayer(layer);
            });

            var getGeomNode = function (branch) {
                var geomNode = null;
                _.each(branch.nodes(), function(node) {
                    if (node.entitytypeid() === self.dataKey) {
                        geomNode = node;
                    }
                });
                return geomNode;
            };

            this.baseLayers = map.baseLayers;

            BranchList.prototype.initialize.apply(this, arguments);

            self.addDefaultNode(self.dataKey, '')

            var style = function (feature) {
                var editing = feature.get('editing');
                return [new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: 'rgba(92, 184, 92, 0.5)'
                    }),
                    stroke: new ol.style.Stroke({
                        color: '#5cb85c',
                        width: editing ? 4 : 2
                    }),
                    image: new ol.style.Circle({
                        radius: editing ? 9 : 7,
                        fill: new ol.style.Fill({
                            color: 'rgba(92, 184, 92, 0.5)'
                        }),
                        stroke: new ol.style.Stroke({
                            color: '#5cb85c',
                            width: editing ? 4 : 2
                        })
                    })
                })];
            }

            var featureOverlay = new ol.FeatureOverlay({
                style: style
            });

            var zoomToFeatureOverlay = function () {
                var extent = null;
                _.each(featureOverlay.getFeatures().getArray(), function(feature) {
                    var featureExtent = feature.getGeometry().getExtent();
                    if (!extent) {
                        extent = featureExtent;
                    } else {
                        extent = ol.extent.extend(extent, featureExtent);
                    }
                });

                if (extent) {
                    map.map.getView().fitExtent(extent, (map.map.getSize()));
                }
            }

            var refreshFreatureOverlay = function () {
                featureOverlay.getFeatures().clear();
                _.each(self.getBranchLists(), function(branch) {
                    var geom = wkt.readGeometry(getGeomNode(branch).value());
                    geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
                    var feature = new ol.Feature({
                        geometry: geom,
                        branch: branch,
                        editing: branch.editing()
                    });

                    branch.editing.subscribe(function () {
                        feature.set('editing', branch.editing());
                        map.map.render();
                    });

                    feature.on('change', function () {
                        var cloneFeature = feature.clone();
                        var geom = cloneFeature.getGeometry();
                        geom.transform(ol.proj.get('EPSG:3857'), ol.proj.get('EPSG:4326'));
                        getGeomNode(branch).value(wkt.writeGeometry(geom));
                        self.removeEditedBranch();
                        branch.editing(true);
                        self.trigger('change', 'geometrychange', branch);
                        self.trigger('geometrychange', feature, wkt.writeGeometry(geom));
                    });
                    try { 
                        featureOverlay.addFeature(feature);
                        }
                    catch(err) {
                        console.log(err.message);
                        }
                });
            }

            self.viewModel.branch_lists.subscribe(refreshFreatureOverlay);
            refreshFreatureOverlay();
            zoomToFeatureOverlay();

            this.on('formloaded', function(){
                map.map.updateSize()
            });

            var draw = null;

            self.$el.find(".geometry-btn").click(function (){ 
                var geometryType = $(this).data('geometrytype');
                if (draw) {
                    map.map.removeInteraction(draw);
                }
                draw = new ol.interaction.Draw({
                    features: featureOverlay.getFeatures(),
                    type: geometryType
                });
                draw.on('drawend', function(e) {
                    addFeature(e.feature, true);
                    map.map.removeInteraction(draw);
                });
                map.map.addInteraction(draw);

                self.$el.find("#inventory-home").click();
            });

            self.$el.find("#inventory-home").click(function (){ 
                self.$el.find("#overlay-panel").addClass("hidden");
                self.$el.find("#basemaps-panel").addClass("hidden");

                self.$el.find("#inventory-basemaps").removeClass("arches-map-tools-pressed");
                self.$el.find("#inventory-basemaps").addClass("arches-map-tools");

                self.$el.find("#inventory-overlays").removeClass("arches-map-tools-pressed");
                self.$el.find("#inventory-overlays").addClass("arches-map-tools");


                self.$el.find("#inventory-home").addClass("arches-map-tools-pressed");
                self.$el.find("#inventory-home").removeClass("arches-map-tools");
                
                return false;
            });
            self.$el.find("#inventory-basemaps").click(function (){ 
                self.$el.find("#overlay-panel").addClass("hidden");
                self.$el.find("#basemaps-panel").removeClass("hidden");

                self.$el.find("#inventory-home").removeClass("arches-map-tools-pressed");
                self.$el.find("#inventory-home").addClass("arches-map-tools");

                self.$el.find("#inventory-overlays").removeClass("arches-map-tools-pressed");
                self.$el.find("#inventory-overlays").addClass("arches-map-tools");

                self.$el.find("#inventory-basemaps").addClass("arches-map-tools-pressed");
                self.$el.find("#inventory-basemaps").removeClass("arches-map-tools");
                
                return false;
            });

            self.$el.find("#inventory-overlays").click(function (){ 
                self.$el.find("#overlay-panel").removeClass("hidden");
                self.$el.find("#basemaps-panel").addClass("hidden");

                self.$el.find("#inventory-home").removeClass("arches-map-tools-pressed");
                self.$el.find("#inventory-home").addClass("arches-map-tools");

                self.$el.find("#inventory-basemaps").removeClass("arches-map-tools-pressed");
                self.$el.find("#inventory-basemaps").addClass("arches-map-tools");

                self.$el.find("#inventory-overlays").addClass("arches-map-tools-pressed");
                self.$el.find("#inventory-overlays").removeClass("arches-map-tools");

                return false;
            });

            this.$el.find(".close").click(function (){ 
                $("#inventory-home").click()
            });

            $(".basemap").click(function (){
                var basemap = $(this).attr('id');
                _.each(map.baseLayers, function(baseLayer){
                    baseLayer.layer.setVisible(baseLayer.id == basemap);
                });
                $("#inventory-home").click()
            });

            var formatConstructors = [
                ol.format.GPX,
                ol.format.GeoJSON,
                ol.format.KML
            ];

            this.$el.find('.geom-upload').on('change', function() {
                if (this.files.length > 0) {
                    var file = this.files[0];
                    var reader = new FileReader();
                    reader.onloadend = function(e) { 
                        var features = [];
                        var result = this.result;
                        _.each(formatConstructors, function(formatConstructor) {
                            var format = new formatConstructor();
                            var readFeatures;
                            try {
                                readFeatures = format.readFeatures(result);
                            } catch (e) {
                                readFeatures = null;
                            }
                            if (readFeatures !== null) {
                                _.each(readFeatures, function (feature) {
                                    var featureProjection = format.readProjection(result);
                                    var transform = ol.proj.getTransform(featureProjection, ol.proj.get('EPSG:3857'));
                                    var geometry = feature.getGeometry();
                                    if (geometry) {
                                        geometry.applyTransform(transform);
                                    }
                                    features.push(feature);
                                });
                            }
                        });
                        if (features.length > 0) {
                            bulkAddFeatures(features);
                        }
                    };
                    reader.readAsText(file);
                }
            });

            featureOverlay.setMap(map.map);

            var modify = new ol.interaction.Modify({
              features: featureOverlay.getFeatures(),
              deleteCondition: function(event) {
                return ol.events.condition.shiftKeyOnly(event) &&
                    ol.events.condition.singleClick(event);
              }
            });
            map.map.addInteraction(modify);
        },
        getBranchLists: function() {    
            var self = this;
            var branch_lists = [];
            _.each(this.viewModel.branch_lists(), function(list){
                _.each(list.nodes(), function(node) {
                    if (node.entitytypeid() === self.dataKey && node.value() !== '') {
                        branch_lists.push(list);
                    }
                });
            }, this);
            return branch_lists;
        },
        removeEditedBranch: function(){
            var branch = this.getEditedBranch();
            if (branch) {
                branch.editing(false);
            }
            return branch;
        },
    });
});