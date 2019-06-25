define([
    'underscore',
    'knockout',
    'views/components/search/base-filter',
    'arches',
    'views/components/widgets/map',
],
function(_, ko, BaseFilter, arches) {
    var componentName = 'map-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                options.name = "Map Filter";
                BaseFilter.prototype.initialize.call(this, options);
                
                this.aggregations = ko.observable();
                this.searchBuffer = ko.observable();
                this.searchResults.timestamp.subscribe(function(timestamp) {
                    this.updateResults();
                }, this);

                this.resizeOnChange = ko.computed(function() {
                    return ko.unwrap(options.resizeOnChange);
                });
                this.filter.feature_collection = ko.observable({
                    "type": "FeatureCollection",
                    "features": []
                });
                this.filter.inverted = ko.observable(false);
                var basemaps = _.filter(arches.mapLayers, function(layer) {
                    return !layer.isoverlay;
                });

                if (!this.defaultBasemap) {
                    this.defaultBasemap = _.find(basemaps, function (basemap) {
                        return basemap.addtomap;
                    });
                }
                if (!this.defaultBasemap) {
                    this.defaultBasemap = basemaps[0];
                }

                this.geocoderDefault = arches.geocoderDefault;

                this.overlays = _.filter(arches.mapLayers, function(layer) {
                    return layer.isoverlay && layer.addtomap;
                }).map(function(layer) {
                    return {
                        'maplayerid': layer.maplayerid,
                        'name': layer.name,
                        'opacity': 100
                    };
                });

                this.defaultZoom = arches.mapDefaultZoom;
                this.minZoom = arches.mapDefaultMinZoom;
                this.maxZoom = arches.mapDefaultMaxZoom;
                this.defaultCenter = [arches.mapDefaultX, arches.mapDefaultY];

                this.clearSearch = ko.observable();
                this.clearSearch.subscribe(function(val) {
                    if (!val) {
                        this.clear(false);
                    }
                }, this);

                this.filters[componentName](this);
                this.restoreState();
                
                var filterUpdated = ko.computed(function() {
                    return JSON.stringify(ko.toJS(this.filter.feature_collection())) + this.filter.inverted();
                }, this);
                filterUpdated.subscribe(function() {
                    this.updateQuery();
                }, this);
            },

            updateQuery: function(filterParams) {
                var self = this;
                var queryObj = this.query();
                if (this.filter.feature_collection().features.length > 0) {
                    if (this.getFilter('term-filter').hasTag(this.type) === false) {
                        this.getFilter('term-filter').addTag('Map Filter Enabled', this.name, this.filter.inverted);
                    }
                    this.filter.feature_collection().features[0].properties['inverted'] = this.filter.inverted();
                    queryObj[componentName] = ko.toJSON(this.filter.feature_collection());
                } else {
                    //this.clear();
                    delete queryObj[componentName];
                }
                this.query(queryObj);
            },

            restoreState: function() {
                var query = this.query();
                if (componentName in query) {
                    var mapQuery = JSON.parse(query[componentName]);
                    if (mapQuery.features.length > 0) {
                        this.filter.inverted(mapQuery.features[0].properties.inverted);
                        this.getFilter('term-filter').addTag('Map Filter Enabled', this.name, this.filter.inverted);
                        this.filter.feature_collection(mapQuery);
                    }
                }
                this.updateResults();
            },

            updateResults: function() {
                if (!!this.searchResults.results){
                    this.aggregations({
                        results: this.searchResults.results.hits.hits,
                        geo_aggs: this.searchResults.results.aggregations.geo_aggs.inner.buckets[0]
                    });
                }
                if(!!this.searchResults[componentName]) {
                    this.searchBuffer(this.searchResults[componentName].search_buffer);
                }
            },

            clear: function(reset_features) {
                if (reset_features !== false){
                    if (this.filter.feature_collection().features.length > 0) {
                        this.filter.feature_collection({
                            "type": "FeatureCollection",
                            "features": []
                        });
                    }
                }
                this.getFilter('term-filter').removeTag('Map Filter Enabled');
            }
        }),
        template: { require: 'text!templates/views/components/search/map-filter.htm' }
    });
});
