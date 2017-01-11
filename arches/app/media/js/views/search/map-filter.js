define([
    'knockout',
    'views/search/base-filter',
    'widgets/map'
],
function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);

            this.resizeOnChange = ko.computed(function() {
                return ko.unwrap(options.resizeOnChange);
            });

            this.filter.feature_collection = ko.observable({
              "type": "FeatureCollection",
              "features": []
            });
        },

        restoreState: function(query) {
            var doQuery = false;
            if ('mapFilter' in query) {
                query.mapFilter = JSON.parse(query.mapFilter);
                if (query.mapFilter.features.length > 0) {
                    console.log('restore query')
                    this.filter.feature_collection(query.mapFilter);
                }
                doQuery = true;
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
            filterParams.mapFilter = ko.toJSON(this.filter.feature_collection());
            return this.filter.feature_collection().features.length === 0;
        }

    });
});
