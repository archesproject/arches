define([
    'knockout',
    'views/components/search/base-filter',
    'arches',
    'views/components/widgets/map',
],
function(ko, BaseFilter, arches) {
    return ko.components.register('map-filter', {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                options.name = "Map Filter";
                BaseFilter.prototype.initialize.call(this, options);
                
                this.aggregations = ko.observable();
                this.searchBuffer = ko.observable();
                this.searchResults.timestamp.subscribe(function(timestamp) {
                    this.aggregations({
                        results: this.searchResults.results.hits.hits,
                        geo_aggs: this.searchResults.results.aggregations.geo_aggs.inner.buckets[0]
                    });
                    this.searchBuffer(this.searchResults.search_buffer);
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

                options.filters['map-filter'](this);
            },

            restoreState: function() {
                var inverted;
                var query = this.query();
                if ('mapFilter' in query) {
                    query.mapFilter = JSON.parse(query.mapFilter);
                    //this.query = query.mapFilter;
                    if (query.mapFilter.features.length > 0) {
                        this.filter.feature_collection(query.mapFilter);
                        this.filter.inverted(query.features[0].properties.inverted);
                        this.termFilter.addTag('Map Filter Enabled', this.name, this.filter.inverted);
                    }
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
                this.termFilter.removeTag('Map Filter Enabled');
            },

            appendFilters: function(filterParams) {
                if (this.filter.feature_collection().features.length > 0) {
                    if (this.termFilter.hasTag(this.type) === false) {
                        this.termFilter.addTag('Map Filter Enabled', this.name, this.filter.inverted);
                    }
                    this.filter.feature_collection().features[0].properties['inverted'] = this.filter.inverted();
                    filterParams.mapFilter = ko.toJSON(this.filter.feature_collection());
                } else {
                    this.clear();
                }
                return this.filter.feature_collection().features.length === 0;
            }
        }),
        template: { require: 'text!templates/views/components/search/map-filter.htm' }
    });
});
