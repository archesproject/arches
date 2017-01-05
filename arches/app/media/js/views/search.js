require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'viewmodels/alert',
    'views/search/base-filter',
    'views/search/time-filter',
    'views/search/term-filter',
    'views/search/map-filter',
    'views/search/search-results',
    'views/base-manager'
], function($, _, ko, arches, AlertViewModel, BaseFilter, TimeFilter, TermFilter, MapFilter, SearchResults, BaseManagerView) {

    var SearchView = BaseManagerView.extend({
        initialize: function(options) {
            var self = this;
            this.filters = {
                termFilter: new TermFilter(),
                timeFilter: new TimeFilter(),
                mapFilter: new MapFilter(),
                savedSearches: new BaseFilter(),
                advancedFilter: new BaseFilter(),
                searchRelatedResources: new BaseFilter()
            };
            _.extend(this.viewModel, this.filters);

            this.viewModel.searchResults = new SearchResults({
                viewModel: this.viewModel
            });

            this.viewModel.selectedTab = ko.observable(this.filters.mapFilter);

            self.isNewQuery = true;

            this.queryString = ko.pureComputed(function() {
                var params = {
                    page: self.viewModel.searchResults.page(),
                    include_ids: self.isNewQuery,
                    no_filters: true
                };
                _.each(self.filters, function (filter) {
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

        getSearchQuery: function() {
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
            } else {
                query.page = 1;
            }
            this.viewModel.searchResults.restoreState(query.page);

            _.each(this.filters, function (filter) {
                filter.restoreState(query)
            });

            this.doQuery();
        },

        clear: function() {
            _.each(this.filters, function (filter) {
                filter.clear();
            });
        }
    });

    return new SearchView();
});
