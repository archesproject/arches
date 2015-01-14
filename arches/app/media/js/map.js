require([
    'jquery',
    'underscore',
    'backbone',
    'openlayers',
    'knockout',
    'arches',
    'layer-info',
    'views/map',
    'map/layers',
    'map/resource-layers',
    'selected-resource-id',
    'bootstrap',
    'select2',
    'plugins/jquery.knob.min'
], function($, _, Backbone, ol, ko, arches, layerInfo, MapView, layers, resourceLayers, selectedResourceId) {
    var geoJSON = new ol.format.GeoJSON();
    var PageView = Backbone.View.extend({
        el: $('body'),
        events: {
            'click .visibility-toggle': 'visibilityToggle',
            'click .on-map-toggle': 'onMapToggle',
            'click .layer-zoom': 'layerZoom'
        },
        initialize: function(options) { 
            var self = this;
            var mapLayers = [];
            _.each(layers, function(layer, index) {
                if (layer.onMap) {
                    mapLayers.push(layer.layer);
                }
                layer.onMap = ko.observable(layer.onMap);
                layers[index].onMap.subscribe(function(add) {
                    if (add) {
                        map.map.addLayer(layer.layer);
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
            self.viewModel = {
                baseLayers: map.baseLayers,
                layers: ko.observableArray(layers),
                filterTerms: ko.observableArray(),
                zoom: ko.observable(arches.mapDefaults.zoom),
                mousePosition: ko.observable(''),
                selectedResource: ko.observable(null),
                selectedAddress: ko.observable('')
            };
            self.map = map;
            selectFeatureIfDefault = function (feature) {
                if (feature.getId() === selectedResourceId) {
                    map.map.getView().fitExtent(feature.getGeometry().getExtent(), map.map.getSize());
                    map.select.getFeatures().clear();
                    map.select.getFeatures().push(feature);
                }
            };
            if (selectedResourceId) {
                _.each(resourceLayers.features(), selectFeatureIfDefault);

                resourceLayers.features.subscribe(function (features) {
                    var feature = features[features.length-1];
                    selectFeatureIfDefault(feature);
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
                var layerModel = {
                      id: _.uniqueId('layer'),
                      name: name,
                      description: '',
                      categories: [''],
                      icon: 'fa fa-map-marker',
                      layer: layer,
                      onMap:  ko.observable(true),
                      active: ko.observable(true),
                      filtered: ko.observable(false)
                };
                layerModel.onMap.subscribe(function(add) {
                    if (add) {
                        map.map.addLayer(layer);
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
                        layer.layer.setOpacity(value/100)
                    }
                });
                $(".knob").css("font-size", 11);
                $(".knob").css("font-weight", 200);
            });

            map.on('viewChanged', function (zoom, extent) {
                self.viewModel.zoom(zoom);
            });

            map.on('mousePositionChanged', function (mousePosition) {
                self.viewModel.mousePosition(mousePosition);
            });

            $('.resource-info-closer').click(function() {
                $('#resource-info').hide();
                map.select.getFeatures().clear();
                $('.resource-info-closer')[0].blur();
            });

            map.select.getFeatures().on('change:length', function(e) {
                if (e.target.getArray().length === 0) {
                    $('#resource-info').hide();
                } else {
                    var clickFeature = e.target.getArray()[0];
                    var keys = clickFeature.getKeys();
                    if (!_.contains(keys, 'select_feature')) {
                        _.defer(function () {
                            map.select.getFeatures().clear();
                            if (_.contains(keys, 'entitytypeid')) {
                                var resourceData = {
                                    id: clickFeature.getId(),
                                    reportLink: arches.urls.reports + clickFeature.getId()
                                };
                                var typeInfo = layerInfo[clickFeature.get('entitytypeid')];
                                var selectFeature = clickFeature.clone();
                                var geom = geoJSON.readGeometry(clickFeature.get('geometry_collection'));
                                if (typeInfo) {
                                    resourceData.typeName = typeInfo.name;
                                    resourceData.typeIcon = typeInfo.icon;
                                }
                                _.each(clickFeature.getKeys(), function (key) {
                                    resourceData[key] = clickFeature.get(key);
                                });
                                geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
                                selectFeature.setGeometry(geom);
                                selectFeature.set('select_feature', true);
                                selectFeature.set('entityid', clickFeature.getId());
                                map.select.getFeatures().push(selectFeature);

                                self.viewModel.selectedResource(resourceData);
                                $('#resource-info').show();
                            }
                        });
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
            $("#inventory-basemaps").click(function (){
                if ($(this).hasClass('arches-map-tools-pressed')) {
                    hideAllPanels();
                } else {
                    $("#overlay-panel").addClass("hidden");
                    $("#basemaps-panel").removeClass("hidden");

                    //Update state of remaining buttons
                    $("#inventory-overlays").removeClass("arches-map-tools-pressed");
                    $("#inventory-overlays").addClass("arches-map-tools");
                    $("#inventory-overlays").css("border-bottom-right-radius", "5px");

                    //Update state of current button and adjust position
                    $("#inventory-basemaps").addClass("arches-map-tools-pressed");
                    $("#inventory-basemaps").removeClass("arches-map-tools");
                    $("#inventory-basemaps").css("border-bottom-left-radius", "5px");
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
                $( "#map-panel" ).slideToggle(600);
                $( "#layer-library" ).slideToggle(600);
            });

            $("#back-to-map").click(function(){
                $( "#map-panel" ).slideToggle(600);
                $( "#layer-library" ).slideToggle(600);
            });

            $('.knob').knob({
                change: function (value) {
                    var layerId = this.$.data().layerid;
                    var layer = ko.utils.arrayFirst(self.viewModel.layers(), function(item) {
                        return layerId === item.id;
                    });
                    layer.layer.setOpacity(value/100)
                }
            });
            $(".knob").css("font-size", 11);
            $(".knob").css("font-weight", 200);

            $(".ol-zoom").css("top", "70px");
            $(".ol-attribution").css("margin-bottom", "70px")

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
                            }
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

                placeholder: "Find an Address or Parcel Number",
                minimumInputLength: 4,
                multiple: true,
                maximumSelectionSize: 1
            });

            $('.geocodewidget').on("select2-selecting", function(e) {
                var geom = geoJSON.readGeometry(e.object.geometry)
                geom.transform(ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
                self.map.map.getView().fitExtent(geom.getExtent(), self.map.map.getSize());
                self.viewModel.selectedAddress(e.object.text)
                overlay.setPosition(ol.extent.getCenter(geom.getExtent()));
                overlay.setPositioning('bottom-center');
                $('#popup').show();
            });

            $('.geocodewidget').on('select2-removing', function () {
                $('#popup').hide();
            });

            var overlay = new ol.Overlay({
              element: $('#popup')[0]
            });

            map.map.addOverlay(overlay);
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
                this.map.map.getView().fitExtent(layer.getSource().getExtent(), this.map.map.getSize());
            }
        }
    });
    new PageView();
});