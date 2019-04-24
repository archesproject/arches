define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'viewmodels/alert',
    'search-components',
    'views/components/search/base-filter',
    'views/components/search/time-filter',
    'views/components/search/term-filter',
    'views/components/search/map-filter',
    'views/components/search/provisional-filter',
    'views/components/search/advanced-search',
    'views/components/search/resource-type-filter',
    'views/resource/related-resources-manager',
    'views/components/search/search-results',
    'views/components/search/saved-searches',
    'views/base-manager',
    'view-data',
    'search-data',
    'views/components/simple-switch'
], function($, _, ko, koMapping, arches, AlertViewModel, SearchComponents, BaseFilter, TimeFilter, TermFilter, MapFilter, ProvisionalFilter, AdvancedSearch, ResourceTypeFilter, RelatedResourcesManager, SearchResults, SavedSearches, BaseManagerView, viewData, searchData) {
    // a method to track the old and new values of a subscribable
    // from https://github.com/knockout/knockout/issues/914
    //
    // use case:
    // var sub1 = this.FirstName.subscribeChanged(function (newValue, oldValue) {
    //     this.NewValue1(newValue);
    //     this.OldValue1(oldValue);
    // }, this);

    ko.subscribable.fn.subscribeChanged = function(callback, context) {
        var savedValue = this.peek();
        return this.subscribe(function(latestValue) {
            var oldValue = savedValue;
            savedValue = latestValue;
            callback.call(context, latestValue, oldValue);
        });
    };

    // var BaseSharedObject = function(params) {
    //     return this.apply(this, params);
    // };


    var getQueryObject = function() {
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
        return query;
    };

    var CommonSearchViewModel = function() {
        this.filters = {};
        searchData.search_components.forEach(function(componentName){
            this.filters[componentName] = ko.observable(null);
        }, this);
        this.tags = ko.observableArray();
        this.selectedTab = ko.observable('map-filter');
        this.resultsExpanded = ko.observable(true);
        this.queryString = ko.observable(JSON.stringify(getQueryObject()));
        this.page = ko.observable(1);
        this.searchBuffer = ko.observable();
        this.aggregations = ko.observable();
        // this.getFilter = function(filterName) {
        //     return this.filter
        // };
    };

    var SearchResultsObject = function() {
        this.mouseoverInstanceId = ko.observable();
        this.mapLinkData = ko.observable(null);
        this.results = koMapping.fromJS({});
        this.isResourceRelatable = function(){};
        this.toggleRelationshipCandidacy = function(){};
    };



    // var MapFilterSharedObject = CommonSearchViewModel.extend({
    //     results: new SearchResultsObject()
    // });


    var SearchView = BaseManagerView.extend({
        initialize: function(options) {

            this.viewModel.sharedStateObject = new CommonSearchViewModel();
            this.viewModel.sharedSearchResultsObject = new SearchResultsObject();
            this.viewModel.mapFilterSharedObject = {};
            _.extend(this.viewModel.mapFilterSharedObject, this.viewModel.sharedStateObject, this.viewModel.sharedSearchResultsObject);


            _.extend(this, this.viewModel.sharedStateObject);

            // this.isNewQuery = true;
            // this.viewModel.resultsExpanded = ko.observable(true);
            // this.viewModel.resourceEditorContext = false;
            // this.aggregations = ko.observable();
            // this.searchBuffer = ko.observable();
            // this.filters = {};
            // this.filters.termFilter = new TermFilter();
            // this.filters.timeFilter = new TimeFilter({
            //     termFilter: this.filters.termFilter
            // });
            // this.filters.provisionalFilter = new ProvisionalFilter({
            //     termFilter: this.filters.termFilter
            // });
            // this.filters.resourceTypeFilter = new ResourceTypeFilter({
            //     termFilter: this.filters.termFilter
            // });
            // this.filters.savedSearches = new BaseFilter();
            // this.filters.advancedFilter = new AdvancedSearch({
            //     graphs: viewData.graphs,
            //     nodes: searchData.searchable_nodes,
            //     cards: searchData.resource_cards,
            //     datatypes: searchData.datatypes
            // });
            // this.filters.searchRelatedResources = new BaseFilter();
            // this.filters.mapFilter = new MapFilter({
            //     aggregations: this.aggregations,
            //     resizeOnChange: this.viewModel.resultsExpanded,
            //     termFilter: this.filters.termFilter,
            //     searchBuffer: this.searchBuffer
            // });

            // this.viewModel.resources = this.viewModel.allGraphs();

            // _.extend(this.viewModel, this.filters);
            // this.viewModel.savedSearches = new SavedSearches();
            // this.viewModel.searchResults = new SearchResults({
            //     aggregations: this.aggregations,
            //     searchBuffer: this.searchBuffer,
            //     viewModel: this.viewModel
            // });

            // this.filters.mapFilter.results = this.viewModel.searchResults;

            // this.viewModel.relatedResourcesManager = new RelatedResourcesManager({
            //     searchResults: this.viewModel.searchResults,
            //     resourceEditorContext: this.viewModel.resourceEditorContext,
            //     editing_instance_id: this.viewModel.editingInstanceId,
            //     relationship_types: this.viewModel.relationship_types,
            //     graph: this.viewModel.graph
            // })

            // var resizeFilter = function(duration){
            //     var duration = duration;
            //     return function(){
            //         var resize = function(){
            //             $(window).trigger("resize");
            //         }
            //         setTimeout(resize, duration);
            //     }
            // }

            // this.viewModel.selectedTab = this.viewModel.resourceEditorContext === true ? ko.observable(this.viewModel.relatedResourcesManager) : ko.observable(this.filters.mapFilter);
            // this.viewModel.selectedTab.subscribe(resizeFilter(100));
            // if (this.viewModel.resourceEditorContext === true) {
            //     this.viewModel.openRelatedResources.subscribe(function(val) {
            //         if (val === true) {
            //             resizeFilter(200)
            //         }
            //     })
            // }

            // this.filters.mapFilter.results = this.viewModel.searchResults;

            // this.queryString = ko.computed(function() {
            //     // we used to loop through all the filters but
            //     // that caused this computed to be triggered multiple times
            //     var params = {};

            //     this.filters.termFilter.appendFilters(params);
            //     this.filters.timeFilter.appendFilters(params);
            //     this.filters.resourceTypeFilter.appendFilters(params);
            //     this.filters.mapFilter.appendFilters(params);
            //     this.filters.advancedFilter.appendFilters(params);
            //     this.filters.provisionalFilter.appendFilters(params);

            //     params.no_filters = !Object.keys(params).length;
            //     return params;
            // }, this);

            // this.filters.termFilter.filter.tags.subscribe(function(tags){
            //     _.each(tags, function(tag){
            //         if(tag.status === 'deleted'){
            //             var found = _.find(this.filters.termFilter.filter.tags, function(currentTag){
            //                return tag.value.type === currentTag.type;
            //             }, this)
            //             if(!found){
            //                 _.each(this.filters, function(filter){
            //                     if(filter.name === tag.value.type){
            //                         filter.clear();
            //                     }
            //                 }, this);
            //             }

            //         }
            //     }, this)
            // }, this, "arrayChange");

            // this.restoreState();

            // this.viewModel.searchResults.page.subscribe(function(){
            //     if(this.viewModel.searchResults.userRequestedNewPage()){
            //         this.isNewQuery = false;
            //         this.viewModel.searchResults.userRequestedNewPage(false);
            //         this.doQuery();
            //     }
            // }, this)
        
            filtersLoaded = ko.computed(function(){
                var allLoaded = true;
                _.each(this.filters, function(value, key, list) {
                    if (!value()) {
                        allLoaded = false;
                    }
                });
                return allLoaded;
            }, this);

            filtersLoaded.subscribe(function(allLoaded) {
                if (allLoaded) {
                    console.log('Filters All Loaded');
                    this.restoreState();
                }
            }, this);


            this.queryString.subscribe(function() {
                this.isNewQuery = true;
                //this.viewModel.searchResults.page(1);
                this.doQuery();
            }, this);

            BaseManagerView.prototype.initialize.call(this, options);

            x = this;
        },

        doQuery: function() {
            var queryString = JSON.parse(this.queryString());
            queryString.page = this.page();
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
                    koMapping.fromJS(response, this.viewModel.sharedSearchResultsObject.results);
                    //var data = this.viewModel.searchResults.updateResults(response);
                    this.filters['search-results']().updateResults(response);
                    this.viewModel.alert(false);
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
            var query = getQueryObject();

            this.filters['search-results']().restoreState(query.page);

            // _.each(this.filters, function(filter) {
            //     filter.restoreState(query);
            // });

            this.doQuery();
        },

        clear: function() {
            _.each(this.filters, function(filter) {
                filter.clear();
            });
        }
    });


    return new SearchView();
});
