define([
    'knockout', 
    'geojson-extent',
    'leaflet',
    'utils/report',
    'views/components/map',
    'geojson-extent',
    'views/components/cards/select-feature-layers',
    'viewmodels/widget',
    'bindings/leaflet',
    'bindings/datatable'
], function(ko, geojsonExtent, L, reportUtils, MapComponentViewModel, geojsonExtent, selectFeatureLayersFactory) {
    return ko.components.register('views/components/reports/scenes/location', {
        viewModel: function(params) {
            var self = this;

            Object.assign(self, reportUtils);
            self.map = ko.observable();
            self.selectedAnnotationTileId = ko.observable();
            self.cards = {};
            self.selectedGeometry = params.selectedGeometry || ko.observable();
            self.visible = {
                geometry: ko.observable(true),
                metadata: ko.observable(true),
                locality: ko.observable(true),

            };
            self.locationTableConfig = {
                ...self.defaultTableConfig,
                columns: Array(6).fill(null)
            };
            self.geometryMetadata = undefined;

            const createUnselectedLayers = (source) => {
                const color = '#A020F0';
                const visible = true;
                const strokecolor = '#fff'

                const layers = [{
                    'id': 'unselected-feature-polygon-fill',
                    'type': 'fill',
                    'minzoom': 11,
                    'filter': ['all',[
                        '==', '$type', 'Polygon'
                    ]],
                    'paint': {
                        'fill-color': color,
                        'fill-outline-color': color,
                        'fill-opacity': 0.2
                    },
                    'layout': {
                        'visibility': visible ? 'visible': 'none'
                    }
                },  {
                    'id': 'unselected-feature-polygon-under-stroke',
                    'type': 'line',
                    'minzoom': 11,
                    'filter': ['all',[
                        '==', '$type', 'Polygon'
                    ]],
                    'layout': {
                        'line-cap': 'round',
                        'line-join': 'round',
                        'visibility': visible ? 'visible': 'none'
                    },
                    'paint': {
                        'line-color': strokecolor,
                        'line-width': 4
                    }
                }, {
                    'id': 'unselected-feature-polygon-stroke',
                    'type': 'line',
                    'minzoom': 11,
                    'filter': ['all',[
                        '==', '$type', 'Polygon'
                    ]], 
                    'layout': {
                        'line-cap': 'round',
                        'line-join': 'round',
                        'visibility': visible ? 'visible': 'none'
                    },
                    'paint': {
                        'line-color': color,
                        'line-width': 2
                    }
                }, {
                    'id': 'unselected-feature-line',
                    'type': 'line',
                    'minzoom': 11,
                    'filter': ['all',[
                        '==', '$type', 'LineString'
                    ]],
                    'layout': {
                        'line-cap': 'round',
                        'line-join': 'round',
                        'visibility': visible ? 'visible': 'none'
                    },
                    'paint': {
                        'line-color': color,
                        'line-width': 2
                    }
                }, {
                    'id': 'unselected-feature-point-point-stroke',
                    'type': 'circle',
                    'minzoom': 11,
                    'filter': ['all',[
                        '==', '$type', 'Point'
                    ]],
                    'paint': {
                        'circle-radius': 6,
                        'circle-opacity': 1,
                        'circle-color': '#fff'
                    },
                    'layout': {
                        'visibility': visible ? 'visible': 'none'
                    }
                }, {
                    'id': 'unselected-feature-point',
                    'type': 'circle',
                    'minzoom': 11,
                    'filter': ['all',[
                        '==', '$type', 'Point'
                    ]],
                    'paint': {
                        'circle-radius': 4,
                        'circle-color': color
                    },
                    'layout': {
                        'visibility': visible ? 'visible': 'none'
                    }
                }];

                layers.forEach((layer) => {
                    layer['source'] = source;
                });

                return layers;
            };

            const changeSelectedSource = (layers, source) => {
                layers.forEach(x => {
                    if(x.id.startsWith('select-')){ x.source = source; }
                })
            };

            self.jumpToDesignationGeometry = (row) => {
                self.map().
                    fitBounds(geojsonExtent(row.geometry));
                const source = self.map().getSource('selected-designation')
                if(source) {
                    data = row.geometry;
                } else {
                    self.map().addSource('selected-designation', {
                        type: 'geojson', 
                        data: row.geometry
                    });
                }
                changeSelectedSource(self.layers, 'selected-designation');
            };

            self.prepareMap = (sourceId, geojson) => {
                if(!geojson){
                    return;
                }
                const mapParams = {};
                if (geojson.features.length > 0) {
                    mapParams.bounds = geojsonExtent(geojson);
                    mapParams.fitBoundsOptions = { padding: 20 };
                }
                
                const sourceConfig = {};
                sourceConfig[sourceId] = {
                        'type': 'geojson',
                        'data': geojson
                    };
                mapParams.sources = Object.assign(sourceConfig, mapParams.sources);
                mapParams.layers = [...selectFeatureLayersFactory(
                    '', //resourceid
                    sourceId, //source
                    undefined, //sourceLayer
                    [], //selectedResourceIds
                    true, //visible
                    '#ff2222' //color
                ), ...createUnselectedLayers(sourceId)];
                MapComponentViewModel.apply(self, [Object.assign({},  mapParams,
                    {
                        'activeTab': ko.observable(false),
                        'zoom': null
                    }
                )]);
                
                self.layers = mapParams.layers; 
                self.sources = mapParams.sources;
                self.map = ko.observable();
            };

            self.geojson = Array.isArray(params.geojson) ? params.geojson : [params.geojson];
            self.prepareMap('app-area-map-data', self.geojson?.[0]);

        },
        template: {
            require: 'text!templates/views/components/reports/scenes/location.htm'
        }
    });
});
