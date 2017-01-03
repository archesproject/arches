require([
    'jquery',
    'knockout',
    'arches',
    'viewmodels/alert',
    'views/search/base-filter',
    'views/search/term-filter',
    'views/search/map-filter',
    'views/search/search-results',
    'views/base-manager'
], function($, ko, arches, AlertViewModel, BaseFilter, TermFilter, MapFilter, SearchResults, BaseManagerView) {

    var SearchView = BaseManagerView.extend({
        initialize: function(options) {
            var self = this;

            this.viewModel.termFilter = new TermFilter();
            this.viewModel.timeFilter = new BaseFilter();
            this.viewModel.mapFilter = new MapFilter();
            this.viewModel.savedSearches = new BaseFilter();
            this.viewModel.advancedFilter = new BaseFilter();
            this.viewModel.searchRelatedResources = new BaseFilter();

            this.filters = [
                this.viewModel.termFilter,
                this.viewModel.timeFilter,
                this.viewModel.mapFilter,
                this.viewModel.savedSearches,
                this.viewModel.advancedFilter,
                this.viewModel.searchRelatedResources
            ];

            this.viewModel.searchResults = new SearchResults({
                viewModel: this.viewModel
            });

            this.viewModel.selectedTab = ko.observable(this.viewModel.mapFilter);

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
