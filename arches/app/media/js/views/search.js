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
    'views/search/resource-type-filter',
    'views/search/search-results',
    'views/base-manager'
], function($, _, ko, arches, AlertViewModel, BaseFilter, TimeFilter, TermFilter, MapFilter, ResourceTypeFilter, SearchResults, BaseManagerView) {

    var SearchView = BaseManagerView.extend({
        initialize: function(options) {
            var self = this;
            this.filters = {
                termFilter: new TermFilter(),
                timeFilter: new TimeFilter(),
                resourceTypeFilter: new ResourceTypeFilter(),
                mapFilter: new MapFilter(),
                savedSearches: new BaseFilter(),
                advancedFilter: new BaseFilter(),
                searchRelatedResources: new BaseFilter()
            };
            this.filters.resourceTypeFilter.termFilter = this.filters.termFilter;
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
            }).extend({ deferred: true });

            // this.filters.termFilter.filter.terms.subscribe(function(terms){
            //     _.each(terms, function (term) {
            //         var filtersAdded = filter.appendFilters(params);
            //         if (filtersAdded) {
            //             params.no_filters = false;
            //         }
            //     });
            // }, this);

            // this.filters.resourceTypeFilter.enabled.subscribe(function(enabled){
            //     if(enabled){
            //         this.filters.termFilter.addTag(this.filters.resourceTypeFilter.name, this.filters.resourceTypeFilter.inverted());
            //     }else{
            //         this.filters.termFilter.removeTag(this.filters.resourceTypeFilter.name);
            //     }
            // },this);

            this.restoreState();

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
            // if (this.updateRequest) {
            //     this.updateRequest.abort();
            // }

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
                    this.updateRequest = undefined;
                }
            });
        },

        restoreState: function() {
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

            _.each(this.filters, function (filter) {
                if (filter.restoreState(query)){
                    doQuery = true;
                }
            });

            if (doQuery) {
                this.doQuery();
            }
        },

        clear: function() {
            _.each(this.filters, function (filter) {
                filter.clear();
            });
        }
    });

    return new SearchView();
});
