define([
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
    'views/resource/related-resources-manager',
    'views/search/search-results',
    'views/base-manager'
], function($, _, ko, arches, AlertViewModel, BaseFilter, TimeFilter, TermFilter, MapFilter, ResourceTypeFilter, RelatedResourcesManager, SearchResults, BaseManagerView) {
    // a method to track the old and new values of a subscribable
    // from https://github.com/knockout/knockout/issues/914
    //
    // use case:
    // var sub1 = this.FirstName.subscribeChanged(function (newValue, oldValue) {
    //     this.NewValue1(newValue);
    //     this.OldValue1(oldValue);
    // }, this);

    ko.subscribable.fn.subscribeChanged = function (callback, context) {
        var savedValue = this.peek();
        return this.subscribe(function (latestValue) {
            var oldValue = savedValue;
            savedValue = latestValue;
            callback.call(context, latestValue, oldValue);
        });
    };


    var SearchBaseManagerView = BaseManagerView.extend({
        initialize: function(options) {
            this.isNewQuery = true;
            this.viewModel.resultsExpanded = ko.observable(true);

            this.aggregations = ko.observable();
            this.filters = {};
            this.filters.termFilter = new TermFilter();
            this.filters.timeFilter = new TimeFilter({
                termFilter: this.filters.termFilter
            });
            this.filters.resourceTypeFilter = new ResourceTypeFilter({
                termFilter: this.filters.termFilter
            });
            this.filters.savedSearches = new BaseFilter();
            this.filters.advancedFilter = new BaseFilter();
            this.filters.searchRelatedResources = new BaseFilter()
            this.filters.mapFilter = new MapFilter({
                aggregations: this.aggregations,
                resizeOnChange: this.viewModel.resultsExpanded,
                termFilter: this.filters.termFilter
            });

            _.extend(this.viewModel, this.filters);

            this.viewModel.searchResults = new SearchResults({
                aggregations: this.aggregations,
                viewModel: this.viewModel
            });

            this.filters.mapFilter.results = this.viewModel.searchResults;

            this.viewModel.relatedResourcesManager = new RelatedResourcesManager({
                searchResults: this.viewModel.searchResults,
                resourceEditorContext: this.viewModel.resourceEditorContext,
                editing_instance_id: this.viewModel.editingInstanceId,
                relationship_types: this.viewModel.relationship_types
            })

            this.viewModel.selectedTab = this.viewModel.resourceEditorContext === true ? ko.observable(this.viewModel.relatedResourcesManager) : ko.observable(this.filters.mapFilter);
            if (this.viewModel.resourceEditorContext === true) {
                this.viewModel.openRelatedResources.subscribe(function(val) {
                    if (val === true) {
                        var resize = function(){
                            $(window).trigger("resize");
                        }
                        setTimeout(resize, 200);
                    }
                })
            }

            this.filters.mapFilter.results = this.viewModel.searchResults;

            this.queryString = ko.computed(function() {
                // we used to loop through all the filters but
                // that caused this computed to be triggered multiple times
                var params = {};

                this.filters.termFilter.appendFilters(params);
                this.filters.timeFilter.appendFilters(params);
                this.filters.resourceTypeFilter.appendFilters(params);
                this.filters.mapFilter.appendFilters(params);

                params.no_filters = !Object.keys(params).length;
                return params;
            }, this);

            this.filters.termFilter.filter.tags.subscribe(function(tags){
                _.each(tags, function(tag){
                    if(tag.status === 'deleted'){
                        var found = _.find(this.filters.termFilter.filter.tags, function(currentTag){
                           return tag.value.type === currentTag.type;
                        }, this)
                        if(!found){
                            _.each(this.filters, function(filter){
                                if(filter.name === tag.value.type){
                                    filter.clear();
                                }
                            }, this);
                        }

                    }
                }, this)
            }, this, "arrayChange");

            this.restoreState();

            this.viewModel.searchResults.page.subscribe(function(){
                if(this.viewModel.searchResults.userRequestedNewPage()){
                    this.isNewQuery = false;
                    this.viewModel.searchResults.userRequestedNewPage(false);
                    this.doQuery();
                }
            }, this)

            this.queryString.subscribe(function() {
                this.isNewQuery = true;
                this.viewModel.searchResults.page(1);
                this.doQuery();
            }, this);

            BaseManagerView.prototype.initialize.call(this, options);
        },

        doQuery: function() {
            var queryString = this.queryString();
            queryString.page = this.viewModel.searchResults.page();
            if (this.updateRequest) {
                this.updateRequest.abort();
            }

            this.viewModel.loading(true);

            this.updateRequest = $.ajax({
                type: "GET",
                url: arches.urls.search_results,
                data: queryString,
                context: this,
                success: function(response) {
                    var data = this.viewModel.searchResults.updateResults(response);
                },
                error: function(response, status, error) {
                    if(this.updateRequest.statusText !== 'abort'){
                        this.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, response.responseText));
                    }
                },
                complete: function(request, status) {
                    this.viewModel.loading(false);
                    this.updateRequest = undefined;
                    window.history.pushState({}, '', '?' + $.param(queryString).split('+').join('%20'));
                }
            });
        },

        restoreState: function() {
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


    return SearchBaseManagerView;
});
