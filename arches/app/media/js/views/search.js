define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'viewmodels/alert',
    'search-components',
    'views/base-manager',
    'view-data',
    'search-data',
    'views/components/simple-switch'
], function($, _, ko, koMapping, arches, AlertViewModel, SearchComponents, BaseManagerView, viewData, searchData) {
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
        this.filtersList = SearchComponents;
        SearchComponents.forEach(function(component) {
            this.filters[component.componentname] = ko.observable(null);
        }, this);
        this.tags = ko.observableArray();
        this.selectedTab = ko.observable('map-filter');
        this.resultsExpanded = ko.observable(true);
        this.query = ko.observable(getQueryObject());
        this.page = ko.observable(1);
        // this.getFilter = function(filterName) {
        //     return this.filter
        // };
        this.mouseoverInstanceId = ko.observable();
        this.mapLinkData = ko.observable(null);
        this.searchResults = {'timestamp': ko.observable()};
        this.isResourceRelatable = function(){};
        this.toggleRelationshipCandidacy = function(){};
    };

    var SearchView = BaseManagerView.extend({
        initialize: function(options) {

            this.viewModel.sharedStateObject = new CommonSearchViewModel();
            _.extend(this, this.viewModel.sharedStateObject);
        
            var filtersLoaded = ko.computed(function(){
                var allLoaded = true;
                var filters = _.filter(this.filters, function(filter, key) {
                    return _.find(this.filtersList, function(f) {
                        return f.enabled && f.componentname === key;
                    }, this);
                }, this);
                _.each(filters, function(value, key, list) {
                    if (!value()) {
                        allLoaded = false;
                    }
                });
                return allLoaded;
            }, this);

            filtersLoaded.subscribe(function(allLoaded) {
                if (allLoaded) {
                    console.log('Filters All Loaded');
                    this.doQuery();
                }
            }, this);

            this.queryString = ko.computed(function() {
                return JSON.stringify(this.query());
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
                    _.each(response, function(value, key, response) {
                        if (key !== 'timestamp') {
                            this.viewModel.sharedStateObject.searchResults[key] = value;
                        }
                    }, this);
                    this.viewModel.sharedStateObject.searchResults.timestamp(response.timestamp);
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

        clear: function() {
            _.each(this.filters, function(filter) {
                filter.clear();
            });
        }
    });


    return new SearchView();
});
