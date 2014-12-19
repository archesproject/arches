require([
    'jquery',
    'underscore',
    'backbone',
    'openlayers',
    'knockout',
    'arches',
    'views/map',
    'map/layers',
    'bootstrap',
    'select2',
    'plugins/jquery.knob.min'
], function($, _, Backbone, ol, ko, arches, MapView, layers) {
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
                overlays: mapLayers
            });
            self.viewModel = {
                baseLayers: map.baseLayers,
                layers: ko.observableArray(layers),
                filterTerms: ko.observableArray(),
                zoom: ko.observable(arches.mapDefaults.zoom),
                mousePosition: ko.observable(''),
                selectedResource: ko.observable(null)
            };
            self.map = map;


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
                $('.resource-info-closer')[0].blur();
            });

            map.map.on('click', function(e) {
                var pixels = [e.originalEvent.offsetX, e.originalEvent.offsetY];
                var clickFeature;
                map.map.forEachFeatureAtPixel(pixels, function (feature, layer) {
                    if (!_.contains(feature.getKeys(), "features")) {
                        clickFeature = feature;
                    }
                });
                if (clickFeature) {
                    var resourceData = {
                        id: clickFeature.getId()
                    }
                    _.each(clickFeature.getKeys(), function (key) {
                        resourceData[key] = clickFeature.get(key);
                    });

                    self.viewModel.selectedResource(resourceData)
                    $('#resource-info').show();
                }
            });

            map.select.getFeatures().on('change:length', function(e) {
                if (e.target.getArray().length === 0) {
                    $('#resource-info').hide();
                } else {
                    $('#resource-info').show();
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
            });


            //Inventory-overlayss button opens overlay panel
            $("#inventory-overlays").click(function (){
                $("#overlay-panel").removeClass("hidden");
                $("#basemaps-panel").addClass("hidden");

                //Update state of remaining buttons
                $("#inventory-basemaps").removeClass("arches-map-tools-pressed");
                $("#inventory-basemaps").addClass("arches-map-tools");

                //Update state of current button and adjust position
                $("#inventory-overlays").addClass("arches-map-tools-pressed");
                $("#inventory-overlays").removeClass("arches-map-tools");
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
                data: function() {
                    var data;

                    data = [
                        {id: "1", text: "109 Newhaven Street, Los Angeles, CA"},
                        {id: "2", text: "11243 Western Drive Los Angeles, CA"},
                        {id: "3", text: "2566 Alison Drive, Santa Monica, CA"},
                        {id: "4", text: "34789 Myers Circle, Burbank, CA"},
                        {id: "5", text: "Parcel: 110-445-009"},
                        {id: "6", text: "Parcel: 333-012-987"},
                        {id: "7", text: "Parcel: 13-012-987"}
                    ];

                    return {results: data};
                },
                placeholder: "Find an Address or Parcel Number",
                multiple: true,
                maximumSelectionSize: 1
            });
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