define(['underscore', 'knockout', 'mapbox-gl-draw'], function(_, ko, MapboxDraw) {
    /**
     * A viewmodel used for managing a spatial search filter.
     *
     * @constructor
     * @name MapFilterViewModel
     *
     */
    var MapFilterViewModel = function(params) {
        var self = this;
        this.searchContext = params.searchContext ||  ko.observable(true);
        this.map = params.map;
        this.draw = params.draw;
        this.buffer = ko.observable(0);
        this.bufferUnit = ko.observable('m');
        this.filter = params.filter || {};
        this.filter.inverted = ko.observable(false);
        this.bufferUnits = [{
            name: 'meters',
            val: 'm'
        },{
            name: 'feet',
            val: 'ft'
        }];

        this.searchContext.subscribe(function(val) {
            if (val === false) {
                self.clear();
            }
        });

        this.filter.feature_collection = ko.observable({
            "type": "FeatureCollection",
            "features": []
        });

        this.searchGeometries = ko.observableArray(null);
        this.sources = {
            "geojson-search-buffer-data": {
                "type": "geojson",
                "generateId": true,
                "data": {
                    "type": "FeatureCollection",
                    "features": []
                }
            }
        };

        this.layers = ko.observable(
            [
                {
                    "id": "geojson-search-buffer-outline-base",
                    "source": "geojson-search-buffer-data",
                    "type": "line",
                    "filter": [
                        "==", "$type", "Polygon"
                    ],
                    "layout": {
                        "line-cap": "round",
                        "line-join": "round"
                    },
                    "paint": {
                        "line-color": "#aa0000",
                        "line-width": 4
                    }
                },
                {
                    "id": "geojson-search-buffer-outline",
                    "source": "geojson-search-buffer-data",
                    "type": "line",
                    "filter": [
                        "==", "$type", "Polygon"
                    ],
                    "layout": {
                        "line-cap": "round",
                        "line-join": "round"
                    },
                    "paint": {
                        "line-color": "#aa0000",
                        "line-width": 2
                    }
                },
                {
                    "id": "geojson-search-buffer-line",
                    "source": "geojson-search-buffer-data",
                    "type": "line",
                    "filter": [
                        "==", "$type", "LineString"
                    ],
                    "layout": {
                        "line-cap": "round",
                        "line-join": "round"
                    },
                    "paint": {
                        "line-color": "#aa0000",
                        "line-width": 2
                    }
                },
                {
                    "id": "geojson-search-buffer",
                    "type": "fill",
                    "filter": [
                        "==", ["geometry-type"], "Polygon"
                    ],
                    "layout": {
                        "visibility": "visible"
                    },
                    "paint": {
                        "fill-color": "#aa3322",
                        "fill-outline-color": "#aa0000",
                        "fill-opacity": 0.2
                    },
                    "source": "geojson-search-buffer-data"
                },
                {
                    "id": "geojson-search-buffer-point-stroke",
                    "type": "circle",
                    "filter": ["==", "$type", "Point"],
                    "paint": {
                        "circle-radius": 6,
                        "circle-opacity": 1,
                        "circle-color": "#fff"
                    },
                    "source": "geojson-search-buffer-data",
                },
                {
                    "id": "geojson-search-buffer-point",
                    "type": "circle",
                    "filter": ["==", "$type", "Point"],
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "#aa0000"
                    },
                    "source": "geojson-search-buffer-data",
                },
            ]
        );

        this.clear = function() {
            this.map().getSource('geojson-search-buffer-data').setData({
                "type": "FeatureCollection",
                "features": []
            });
            this.draw.getAll().features.forEach(function(feature){
                if (feature.properties.searchGeom) {
                    self.draw.delete(feature.id);
                }
            });
            this.searchGeometries([]);
        };

        this.spatialFilterTypes = [{
            name: 'Point',
            title: 'Draw a Marker',
            class: 'leaflet-draw-draw-marker',
            icon: 'ion-location',
            drawMode: 'draw_point',
            active: ko.observable(false)
        }, {
            name: 'Line',
            title: 'Draw a Polyline',
            icon: 'ion-steam',
            class: 'leaflet-draw-draw-polyline',
            drawMode: 'draw_line_string',
            active: ko.observable(false)
        }, {
            name: 'Polygon',
            title: 'Draw a Polygon',
            icon: 'fa fa-pencil-square-o',
            class: 'leaflet-draw-draw-polygon',
            drawMode: 'draw_polygon',
            active: ko.observable(false)
        }];

        this.drawMode = ko.observable();
        this.drawModes = _.pluck(this.spatialFilterTypes, 'drawMode');
        this.drawMode.subscribe(function(selectedDrawTool){
            if(!!selectedDrawTool){
                if(selectedDrawTool === 'extent'){
                    this.searchByExtent();
                } else {
                    this.draw.changeMode(selectedDrawTool);
                }
            }
        }, this);
        
        this.useMaxBuffer = function(unit, buffer, maxBuffer) {
            var res = false;
            if (unit === 'ft') {
                res = (buffer * 0.3048) > maxBuffer;
            } else {
                res = buffer > maxBuffer;
            }
            return res;
        };

        this.setupDraw = function() {
            var self = this;
            if (!this.draw) {
                var modes = MapboxDraw.modes;
                modes.static = {
                    toDisplayFeatures: function(state, geojson, display) {
                        display(geojson);
                    }
                };
                this.draw = new MapboxDraw({
                    displayControlsDefault: false,
                    modes: modes
                });
                this.map().addControl(this.draw);
            }
            this.map().on('draw.create', function(e) {
                if (self.searchContext()) {
                    self.draw.getAll().features.forEach(function(feature){
                        if(feature.id !== e.features[0].id) {
                            if (feature.properties.searchGeom) {
                                self.draw.delete(feature.id);
                            }
                        } else {
                            self.draw.setFeatureProperty(feature.id, 'nodeId', null);
                            self.draw.setFeatureProperty(feature.id, 'searchGeom', true);
                        }
                    });
                    self.searchGeometries(e.features);
                    self.updateFilter();
                    self.drawMode(undefined);
                }
            });
            this.map().on('draw.update', function(e) {
                if (self.searchContext()) {
                    self.searchGeometries(e.features);
                    self.updateFilter();
                }
            });
        };

        this.makeSearchFeature = function(feature) {
            if (self.searchContext()) {
                self.searchGeometries([feature]);
                self.updateFilter();
            }
        };

        this.updateFilter = function(){
            if (this.buffer() < 0) {
                this.buffer(0);
            }

            var useMaxBuffer = this.useMaxBuffer(this.bufferUnit(), this.buffer(), this.maxBuffer);
            if (useMaxBuffer) {
                var max = this.bufferUnit() === 'ft' ? 328084 : this.maxBuffer;
                this.buffer(max);
            }

            this.searchGeometries().forEach(function(feature){
                if(!feature.properties){
                    feature.properties = {};
                }
                feature.properties.buffer = {
                    "width": this.buffer(),
                    "unit": this.bufferUnit()
                };
                feature.properties.inverted = this.filter.inverted();
            }, this);

            this.filter.feature_collection({
                "type": "FeatureCollection",
                "features": this.searchGeometries()
            });
        };

        this.buffer.subscribe(function() {
            this.updateFilter();
        }, this);

        this.bufferUnit.subscribe(function() {
            this.updateFilter();
        }, this);
        //----------------- End search buffer values from map-filter
        
    };
    return MapFilterViewModel;
});
