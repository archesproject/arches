require([
    'jquery',
    'knockout',
    'arches',
    'viewmodels/alert',
    'views/search/base-filter',
    'views/search/term-filter',
    'views/search/search-results',
    'views/base-manager'
], function($, ko, arches, AlertViewModel, BaseFilter, TermFilter, SearchResults, BaseManagerView) {

    var SearchView = BaseManagerView.extend({
        // updateRequest: '',

        // events: {
        //     'click #view-saved-searches': 'showSavedSearches',
        //     'click #clear-search': 'clear',
        //     'click #map-filter-button': 'toggleMapFilter',
        //     'click #time-filter-button': 'toggleTimeFilter',
        //     'click a.dataexport': 'exportSearch'
        // },

        initialize: function(options) {
            var mapFilterText, timeFilterText;
            var self = this;

            this.viewModel.termFilter = new TermFilter({
                el: $.find('input.resource_search_widget')[0]
            });

            this.viewModel.timeFilter = new BaseFilter({
                //el: $.find('input.resource_search_widget')[0]
            });

            this.viewModel.mapFilter = new BaseFilter({
                //el: $.find('input.resource_search_widget')[0]
            });

            this.filters = [
                this.viewModel.termFilter,
                this.viewModel.timeFilter,
                this.viewModel.mapFilter
            ];

            this.viewModel.searchResults = new SearchResults({
                //el: $('#search-results-container')[0],
                viewModel: this.viewModel
            });
            this.viewModel.searchResults.on('mouseover', function(resourceid) {
                this.viewModel.mapFilter.selectFeatureById(resourceid);
            }, this);
            this.viewModel.searchResults.on('mouseout', function() {
                this.viewModel.mapFilter.unselectAllFeatures();
            }, this);
            this.viewModel.searchResults.on('find_on_map', function(resourceid, data) {
                var extent,
                    expand = !this.viewModel.mapFilter.expanded();
                if (expand) {
                    this.viewModel.mapFilter.expanded(true);
                }

                _.each(data.geometries, function(geometryData) {
                    var geomExtent = wkt.readGeometry(geometryData.label).getExtent();
                    geomExtent = ol.extent.applyTransform(geomExtent, ol.proj.getTransform('EPSG:4326', 'EPSG:3857'));
                    extent = extent ? ol.extent.extend(extent, geomExtent) : geomExtent;
                });
                if (extent) {
                    _.delay(function() {
                        self.viewModel.mapFilter.zoomToExtent(extent);
                    }, expand ? 700 : 0);
                }
            }, this);

            // mapFilterText = this.viewModel.mapFilter.$el.data().filtertext;
            // timeFilterText = this.viewModel.timeFilter.$el.data().filtertext;

            self.isNewQuery = true;

            this.queryString = ko.pureComputed(function() {
                var params = {
                    page: self.viewModel.searchResults.page(),
                    include_ids: self.isNewQuery,
                    no_filters: true
                };
                self.filters.forEach(function(filter) {
                    var filtersAdded = filter.appendFilters(params);
                    if (filtersAdded) {
                        params.no_filters = false;
                    }
                });
                return $.param(params).split('+').join('%20');
            });

            this.getSearchQuery();

            this.viewModel.searchResults.page.subscribe(function() {
                self.doQuery();
            });

            this.queryString.subscribe(function() {
                self.isNewQuery = true;
                self.viewModel.searchResults.page(1);
                self.doQuery();
            });

            BaseManagerView.prototype.initialize.call(this, options);
        },

        doQuery: function() {
            var self = this;
            var queryString = this.queryString();
            if (this.updateRequest) {
                this.updateRequest.abort();
            }

            this.viewModel.loading(true);
            window.history.pushState({}, '', '?' + queryString);

            this.updateRequest = $.ajax({
                type: "GET",
                url: arches.urls.search_results,
                data: queryString,
                context: this,
                success: function(response) {
                    var data = this.viewModel.searchResults.updateResults(response);
                    // this.viewModel.mapFilter.highlightFeatures(data, $('.search-result-all-ids').data('results'));
                    // this.viewModel.mapFilter.applyBuffer();
                    this.isNewQuery = false;
                },
                error: function(response, status, error) {
                    this.viewModel.alert(new AlertViewModel('ep-alert-red', arches.graphImportFailed.title, response));
                },
                complete: function(request, status) {
                    this.viewModel.loading(false);
                }
            });
        },

        showSavedSearches: function() {
            this.clear();
            $('#saved-searches').slideDown('slow');
            $('#search-results').slideUp('slow');
            this.viewModel.mapFilter.expanded(false);
            this.viewModel.timeFilter.expanded(false);
        },

        hideSavedSearches: function() {
            $('#saved-searches').slideUp('slow');
            $('#search-results').slideDown('slow');
        },

        toggleMapFilter: function() {
            if ($('#saved-searches').is(":visible")) {
                this.doQuery();
                this.hideSavedSearches();
            }
            this.viewModel.mapFilter.expanded(!this.viewModel.mapFilter.expanded());
            window.history.pushState({}, '', '?' + this.queryString());
        },

        toggleTimeFilter: function() {
            if ($('#saved-searches').is(":visible")) {
                this.doQuery();
                this.hideSavedSearches();
            }
            this.viewModel.timeFilter.expanded(!this.viewModel.timeFilter.expanded());
            window.history.pushState({}, '', '?' + this.queryString());
        },

        getSearchQuery: function() {
            var doQuery = false;
            var query = _.chain(decodeURIComponent(location.search).slice(1).split('&'))
                // Split each array item into [key, value]
                // ignore empty string if search is empty
                .map(function(item) {
                    if (item) return item.split('=');
                })
                // Remove undefined in the case the search is empty
                .compact()
                // Turn [key, value] arrays into object parameters
                .object()
                // Return the value of the chain operation
                .value();

            if ('page' in query) {
                query.page = JSON.parse(query.page);
                doQuery = true;
            }
            this.viewModel.searchResults.restoreState(query.page);

            this.filters.forEach(function (filter) {
                if (filter.restoreState(query)){
                    doQuery = true;
                }
            });

            if (doQuery) {
                this.doQuery();
                this.hideSavedSearches();
            }

        },

        clear: function() {
            this.filters.forEach(function(filter) {
                filter.clear();;
            });
        }
    });

    return new SearchView();
});
