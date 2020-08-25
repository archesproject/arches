define(['underscore', 'knockout'], function(_, ko) {
    /**
     * A viewmodel used for a generic geocoder
     *
     * @constructor
     * @name MapFilterViewModel
     *
     */
    var MapFilterViewModel = function(params) {
        var self = this;

        this.map = params.map;
        this.draw = params.draw;
        this.buffer = ko.observable(0);
        this.bufferUnit = ko.observable('m');
        this.filter = params.filter || {};
        this.bufferUnits = [{
            name: 'meters',
            val: 'm'
        },{
            name: 'feet',
            val: 'ft'
        }];
        this.filter.feature_collection = ko.observable({
            "type": "FeatureCollection",
            "features": []
        });

        this.filter.feature_collection.subscribe(function(val){
            console.log(val);
        });
        this.searchGeometries = ko.observableArray(null);
        params.sources = {
            "geojson-search-buffer-data": {
                "type": "geojson",
                "generateId": true,
                "data": {
                    "type": "FeatureCollection",
                    "features": []
                }
            }
        };

        params.layers = ko.observable(
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
                        "line-color": "#fff",
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
                        "line-color": "#3bb2d0",
                        "line-width": 2
                    }
                },
                {
                    "id": "geojson-search-buffer",
                    "type": "fill",
                    "layout": {
                        "visibility": "visible"
                    },
                    "paint": {
                        "fill-color": "#3bb2d0",
                        "fill-outline-color": "#3bb2d0",
                        "fill-opacity": 0.2
                    },
                    "source": "geojson-search-buffer-data"
                }
            ]
        );

        this.clear = function() {
            this.filter.feature_collection({
                "type": "FeatureCollection",
                "features": []
            });
            this.map().getSource('geojson-search-buffer-data').setData({
                "type": "FeatureCollection",
                "features": []
            });
            this.getFilter('term-filter').removeTag('Map Filter Enabled');
            this.draw.deleteAll();
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
        
        this.useMaxBuffer = function (unit, buffer, maxBuffer) {
            res = false;
            if (unit === 'ft') {
                res = (buffer * 0.3048) > maxBuffer
            } else {
                res = buffer > maxBuffer
            }
            return res;
        },

        this.updateFilter = function(){
            console.log('updating filter')
            if (this.buffer() < 0) {
                this.buffer(0);
            }

            var useMaxBuffer = this.useMaxBuffer(this.bufferUnit(), this.buffer(), this.maxBuffer);
            var buffer = this.buffer();
            if (useMaxBuffer) {
                max = this.bufferUnit() === 'ft' ? 328084 : this.maxBuffer;
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
        }

        this.buffer.subscribe(function(val) {
            this.updateFilter();
        }, this);

        this.bufferUnit.subscribe(function(val) {
            this.updateFilter();
        }, this);
        //----------------- End search buffer values from map-filter
        

    };
    return MapFilterViewModel;
});
