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
                if (geom.getLayout() === 'XYZ'){ //Dragged&dropped KMLs have XYZ layouts which are read by default by the ol WKT parser. This routine pops the Z values out and flattens the layout to XY
                    var FlatCoordinates = [];
                    if ($.isArray(geom.getCoordinates()[0])) {
                        if ($.isArray(geom.getCoordinates()[0][0])) { //Polygons
                            FlatCoordinates[0] = []; 
                            _.each(geom.getCoordinates()[0], function(coordinate_set){ 
                                    if (coordinate_set.length === 3){
                                        coordinate_set.pop();
                                        FlatCoordinates[0].push(coordinate_set);
                                    }
                            });
                        }else{ //Polylines
                            _.each(geom.getCoordinates(), function(coordinate_set){ 
                                    if (coordinate_set.length === 3){
                                        coordinate_set.pop();
                                        FlatCoordinates.push(coordinate_set);
                                    }
                            });
                        }
                    }else{ //Points
                        FlatCoordinates = geom.getCoordinates();
                        FlatCoordinates.pop();
                        console.log(FlatCoordinates);
                       
                    }
                    geom.setCoordinates(FlatCoordinates, 'XY');
                }
                _.each(branch.nodes(), function(node) {
                    if (node.entitytypeid() === self.dataKey) {
                        node.value(wkt.writeGeometry(geom));
                    }
                });
                self.viewModel.branch_lists.push(branch);
                self.trigger('change', 'geometrychange', branch);
                self.trigger('geometrychange', feature, wkt.writeGeometry(geom));
                
            };
            var object = JSON.parse($('#formdata').val());
            var datesall =[];
            datesall.push(object['SPATIAL_COORDINATES_GEOMETRY.E47']['BingDates']['start']);
            datesall.push(object['SPATIAL_COORDINATES_GEOMETRY.E47']['BingDates']['end']);
            var nonull = _.reject(datesall, function(date) {
                return date ==null;
            });
            var dates = _.uniq(nonull);
            if (dates.length>1) {
                var datestring = dates[0].slice(0,-4) && "/" && dates[0].slice(0,-4);
            }else if (dates.length == 1) {
                    var datestring = dates[0].slice(0,-4);
            }else{
                var datestring = "None"
                
            };
            $("#imagery-date").text(datestring);
            $("#datescontainer").show();

                
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
                        color: 'rgba(92, 184, 92, 0)'
                    }),
                    stroke: new ol.style.Stroke({
                        color: '#b30000',
                        width: editing ? 4 : 3
                    }),
                    image: new ol.style.Circle({
                        radius: editing ? 9 : 7,
                        fill: new ol.style.Fill({
                            color: 'rgba(92, 184, 92, 0)'
                        }),
                        stroke: new ol.style.Stroke({
                            color: '#b30000',
                            width: editing ? 4 : 3
                        })
                    })
                })];
            }
            var features = new ol.Collection();
            var featureOverlay = new ol.layer.Vector({
                source: new ol.source.Vector({
                    features: features
                }),
                style: style
            });

            var zoomToFeatureOverlay = function () {
                var extent = null;
                _.each(featureOverlay.getSource().getFeatures(), function(feature) {
                    var featureExtent = feature.getGeometry().getExtent();
                    if (!extent) {
                        extent = featureExtent;
                    } else {
                        extent = ol.extent.extend(extent, featureExtent);
                    }
                });

                if (extent) {
                    map.map.getView().fit(extent, (map.map.getSize()));
                }
            }

            var refreshFreatureOverlay = function () {
                featureOverlay.getSource().forEachFeature(function(feature) {
                     featureOverlay.getSource().removeFeature(feature);
                });
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
                        featureOverlay.getSource().addFeature(feature);
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
                    features: featureOverlay.getSource().getFeatures(),
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
                $("#inventory-home").click();
                if (basemap ==='Aerial') {
                    $("#imagery-date").text(datestring);
                    $("#datescontainer").show();
                }else {
                    $("#datescontainer").hide()
                };                             
            });

            // take the input lat/long and add to map by making a feature from wkt. Credits @mradamcox: https://github.com/mradamcox/ead/commit/a86540958075ec82812714484e58bd0e9c9ba3de
            this.$el.find('#add-lat-long').on('click', function() {
                var latdd = $('#latinput').val();
                var longdd = $('#longinput').val();
                var wkt = 'POINT('+longdd+' '+latdd+')';
                var format = new ol.format.WKT();
                var feature = format.readFeature(wkt, {
                    dataProjection: 'EPSG:4326',
                    featureProjection: 'EPSG:3857'
                });
                bulkAddFeatures([feature]);
                $("#inventory-home").click();
                $('.coord-input').val("");
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
              features: features,
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