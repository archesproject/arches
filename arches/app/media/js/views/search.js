define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'viewmodels/alert',
    'search-components',
    'views/base-manager',
    'views/components/simple-switch'
], function($, _, ko, koMapping, arches, AlertViewModel, SearchComponents, BaseManagerView) {
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
        return query;
    };

    var CommonSearchViewModel = function() {
        this.filters = {};
        this.filtersList = _.sortBy(SearchComponents, function(filter) {
            return filter.sortorder;
        }, this);
        SearchComponents.forEach(function(component) {
            this.filters[component.componentname] = ko.observable(null);
        }, this);
        var firstEnabledFilter = _.find(this.filtersList, function(filter) {
            return filter.type === 'filter' && filter.enabled === true;
        }, this);
        this.selectedTab = ko.observable(firstEnabledFilter.componentname);
        this.selectedPopup = ko.observable('');
        this.resultsExpanded = ko.observable(true);
        this.query = ko.observable(getQueryObject());
        this.clearQuery = function(){
            Object.values(this.filters).forEach(function(value){
                if (value()){
                    if (value().clear){
                        value().clear();
                    }
                }
            }, this);
            this.query({"paging-filter": "1", tiles: "true"});
        };
        this.filterApplied = ko.pureComputed(function(){
            var self = this;
            var filterNames = Object.keys(this.filters);
            return filterNames.some(function(filterName){
                if (ko.unwrap(self.filters[filterName]) && filterName !== 'paging-filter') {
                    return !!ko.unwrap(self.filters[filterName]).query()[filterName];
                } else {
                    return false;
                }
            });
        }, this);
        this.mouseoverInstanceId = ko.observable();
        this.mapLinkData = ko.observable(null);
        this.userIsReviewer = ko.observable(false);
        this.userid = ko.observable(null);
        this.searchResults = {'timestamp': ko.observable()};
        this.selectPopup = function(componentname) {
            if(this.selectedPopup() !== '' && componentname === this.selectedPopup()) {
                this.selectedPopup('');
            } else {
                this.selectedPopup(componentname);
            }
        };
        this.isResourceRelatable = function(graphId) {
            var relatable = false;
            if (this.graph) {
                relatable = _.contains(this.graph.relatable_resource_model_ids, graphId);
            }
            return relatable;
        };
        this.toggleRelationshipCandidacy = function() {
            var self = this;
            return function(resourceinstanceid){
                var candidate = _.contains(self.relationshipCandidates(), resourceinstanceid);
                if (candidate) {
                    self.relationshipCandidates.remove(resourceinstanceid);
                } else {
                    self.relationshipCandidates.push(resourceinstanceid);
                }
            };
        };
    };

    var SearchView = BaseManagerView.extend({
        initialize: function(options) {
            this.viewModel.sharedStateObject = new CommonSearchViewModel();
            this.viewModel.total = ko.observable();
            _.extend(this, this.viewModel.sharedStateObject);
            this.viewModel.sharedStateObject.total = this.viewModel.total;
            this.viewModel.sharedStateObject.loading = this.viewModel.loading;
            this.queryString = ko.computed(function() {
                return JSON.stringify(this.query());
            }, this);

            this.queryString.subscribe(function() {
                this.doQuery();
            }, this);

            BaseManagerView.prototype.initialize.call(this, options);

            this.doQuery();
        },

        doQuery: function() {
            var queryString = JSON.parse(this.queryString());
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
                    _.each(this.viewModel.sharedStateObject.searchResults, function(value, key, results) {
                        if (key !== 'timestamp') {
                            delete this.viewModel.sharedStateObject.searchResults[key];
                        }
                    }, this);
                    _.each(response, function(value, key, response) {
                        if (key !== 'timestamp') {
                            this.viewModel.sharedStateObject.searchResults[key] = value;
                        }
                    }, this);
                    this.viewModel.sharedStateObject.searchResults.timestamp(response.timestamp);
                    this.viewModel.sharedStateObject.userIsReviewer(response.reviewer);
                    this.viewModel.sharedStateObject.userid(response.userid);
                    this.viewModel.total(response.total_results);
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
        }
    });


    return new SearchView();
});
