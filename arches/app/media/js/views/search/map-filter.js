define([
    'knockout',
    'views/search/base-filter',
    'widgets/map'
],
function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            this.name = "Map Filter";
            this.resizeOnChange = ko.computed(function() {
                return ko.unwrap(options.resizeOnChange);
            });
            this.filter.feature_collection = ko.observable({
              "type": "FeatureCollection",
              "features": []
            });
            this.filter.inverted = ko.observable(false);
        },

        restoreState: function(query) {
            var doQuery = false;
            var inverted;
            if ('mapFilter' in query) {
                query.mapFilter = JSON.parse(query.mapFilter);
                this.query = query.mapFilter;
                if (query.mapFilter.features.length > 0) {
                    this.filter.feature_collection(query.mapFilter);
                    this.filter.inverted(this.query.features[0].properties.inverted)
                    this.termFilter.addTag('Map Filter Enabled', this.name, this.filter.inverted);
                }
                doQuery = true;
            } else {
                this.query = undefined;
            }
            return doQuery;
        },

        clear: function() {
            this.filter.feature_collection({
              "type": "FeatureCollection",
              "features": []
            });
        },

        appendFilters: function(filterParams) {
            if (this.filter.feature_collection().features.length > 0) {
                if (this.termFilter.hasTag(this.type) === false) {
                    this.termFilter.addTag('Map Filter Enabled', this.name, this.filter.inverted);
                };
                this.filter.feature_collection().features[0].properties['inverted'] = this.filter.inverted()
            };
            filterParams.mapFilter = ko.toJSON(this.filter.feature_collection());
            return this.filter.feature_collection().features.length === 0;
        }

    });
});
