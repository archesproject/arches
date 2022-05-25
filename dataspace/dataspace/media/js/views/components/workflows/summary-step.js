define([
    'knockout',
    'views/components/workflows/final-step',
    'geojson-extent',
    'leaflet',
    'views/components/map',
    'views/components/cards/select-feature-layers',
    'viewmodels/alert',
    'bindings/leaflet'
], function(ko, FinalStep, geojsonExtent, L, MapComponentViewModel, selectFeatureLayersFactory, AlertViewModel) {

    function viewModel(params) {
        FinalStep.apply(this, [params]);
        this.resourceData = ko.observable();
        this.relatedResources = ko.observableArray();

        this.getResourceData = function(resourceid, resourceData) {
            window.fetch(this.urls.api_resources(resourceid) + '?format=json&compact=false&v=beta')
            .then(response => response.json())
            .then(data => resourceData(data))
        };

        this.getRelatedResources = function(resourceid, relatedResources) {
            window.fetch(this.urls.related_resources + resourceid + "?paginate=false")
            .then(response => response.json())
            .then(data => relatedResources(data))
        };

        this.init = function(){
            this.getResourceData(this.resourceid, this.resourceData);
            this.getRelatedResources(this.resourceid, this.relatedResources)
        };

        this.getResourceValue = function(obj, attrs, missingValue='none') {
            try {
                return attrs.reduce(function index(obj, i) {return obj[i]}, obj) || missingValue;
            } catch(e) {
                return missingValue;
            }
        };

        this.prepareMap = function(geojson, source) {
            var mapParams = {};
            if (geojson.features.length > 0) {
                mapParams.bounds = geojsonExtent(geojson);
                mapParams.fitBoundsOptions = { padding: 20 };
            }
            var sourceConfig = {};
            sourceConfig[source] = {
                    "type": "geojson",
                    "data": geojson
                };
            mapParams.sources = Object.assign(sourceConfig, mapParams.sources);
            mapParams.layers = selectFeatureLayersFactory(
                '', //resourceid
                source, //source
                undefined, //sourceLayer
                [], //selectedResourceIds
                true, //visible
                '#ff2222' //color
            );
            MapComponentViewModel.apply(this, [Object.assign({},  mapParams,
                {
                    "activeTab": ko.observable(false),
                    "zoom": null
                }
            )]);
        
            this.layers = mapParams.layers;
            this.sources = mapParams.sources;
        };

        this.prepareAnnotation = function(featureCollection) {
            var canvas = featureCollection.features[0].properties.canvas;

            return {
                center: [0, 0],
                crs: L.CRS.Simple,
                zoom: 0,
                afterRender: function(map) {
                    L.tileLayer.iiif(canvas + '/info.json').addTo(map);
                    var extent = geojsonExtent(featureCollection);
                    map.addLayer(L.geoJson(featureCollection, {
                        pointToLayer: function(feature, latlng) {
                            return L.circleMarker(latlng, feature.properties);
                        },
                        style: function(feature) {
                            return feature.properties;
                        }
                    }));
                    L.control.fullscreen().addTo(map);
                    setTimeout(function() {
                        map.fitBounds([
                            [extent[1]-1, extent[0]-1],
                            [extent[3]+1, extent[2]+1]
                        ]);
                    }, 250);
                }
            };
        }

        this.init();
    }
    
    return viewModel;
});
