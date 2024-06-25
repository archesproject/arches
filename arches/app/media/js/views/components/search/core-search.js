define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'viewmodels/alert',
    'views/components/search/base-filter',
    'templates/views/components/search/core-search.htm',
], function($, _, ko, arches, AlertViewModel, BaseFilter, coreSearchTemplate) {
    const componentName = 'core-search';
    const viewModel = BaseFilter.extend({ 
        initialize: function(sharedStateObject) {
            const self = this;
            sharedStateObject.componentName = componentName;
            BaseFilter.prototype.initialize.call(this, sharedStateObject);
            this.query = sharedStateObject.query;
            this.queryString = sharedStateObject.queryString;
            this.updateRequest = sharedStateObject.updateRequest;
            this.userIsReviewer = sharedStateObject.userIsReviewer;
            this.total = sharedStateObject.total;
            this.userid = sharedStateObject.userid;
            this.hits = sharedStateObject.hits;
            this.alert = sharedStateObject.alert;
            this.sharedStateObject = sharedStateObject;
            this.queryString.subscribe(function() {
                this.doQuery();
            }, this);
            this.selectedPopup = ko.observable('');
            this.sharedStateObject.selectedPopup = this.selectedPopup;
            var firstEnabledFilter = _.find(this.sharedStateObject.filtersList, function(filter) {
                return filter.type === 'filter';
            }, this);
            this.selectedTab = ko.observable(firstEnabledFilter.componentname);
            this.sharedStateObject.selectedTab = this.selectedTab;

            this.filterApplied = ko.pureComputed(function(){
                var filterNames = Object.keys(sharedStateObject.filters);
                return filterNames.some(function(filterName){
                    if (ko.unwrap(sharedStateObject.filters[filterName]) && filterName !== 'paging-filter') {
                        return !!ko.unwrap(sharedStateObject.filters[filterName]).query()[filterName];
                    } else {
                        return false;
                    }
                });
            }, this);
            this.resultsExpanded = ko.observable(true);
            this.isResourceRelatable = function(graphId) {
                var relatable = false;
                if (this.graph) {
                    relatable = _.contains(this.graph.relatable_resource_model_ids, graphId);
                }
                return relatable;
            };
            this.sharedStateObject.isResourceRelatable = this.isResourceRelatable;
            this.toggleRelationshipCandidacy = function() {
                return function(resourceinstanceid){
                    var candidate = _.contains(sharedStateObject.relationshipCandidates(), resourceinstanceid);
                    if (candidate) {
                        sharedStateObject.relationshipCandidates.remove(resourceinstanceid);
                    } else {
                        sharedStateObject.relationshipCandidates.push(resourceinstanceid);
                    }
                };
            };
            this.sharedStateObject.toggleRelationshipCandidacy = this.toggleRelationshipCandidacy;

            this.clearQuery = function(){
                Object.values(this.sharedStateObject.filters).forEach(function(value){
                    if (value()){
                        if (value().clear){
                            value().clear();
                        }
                    }
                }, this);
                this.query({"paging-filter": "1", "core":"core-search", tiles: "true"});
            };

            this.selectPopup = function(componentname) {
                if(this.selectedPopup() !== '' && componentname === this.selectedPopup()) {
                    this.selectedPopup('');
                } else {
                    this.selectedPopup(componentname);
                }
            };
            if (this.requiredFiltersLoaded() === false) {
                this.requiredFiltersLoaded.subscribe(function() {
                    this.restoreState();
                }, this);
            } else {
                this.restoreState();
            }
        },

        doQuery: function() {
            let queryObj = JSON.parse(this.queryString());
            queryObj[componentName] = true;
            if (!queryObj["search-results"])
                queryObj["search-results"] = "";
            if (self.updateRequest) { self.updateRequest.abort(); }
            self.updateRequest = $.ajax({
                type: "GET",
                url: arches.urls.search_results,
                data: queryObj,
                context: this,
                success: function(response) {
                    _.each(this.sharedStateObject.searchResults, function(value, key, results) {
                        if (key !== 'timestamp') {
                            delete this.sharedStateObject.searchResults[key];
                        }
                    }, this);
                    _.each(response, function(value, key, response) {
                        if (key !== 'timestamp') {
                            this.sharedStateObject.searchResults[key] = value;
                        }
                    }, this);
                    this.sharedStateObject.searchResults.timestamp(response.timestamp);
                    this.sharedStateObject.userIsReviewer(response.reviewer);
                    this.sharedStateObject.userid(response.userid);
                    this.sharedStateObject.total(response.total_results);
                    this.sharedStateObject.hits(response.results.hits.hits.length);
                    this.sharedStateObject.alert(false);
                },
                error: function(response, status, error) {
                    const alert = new AlertViewModel('ep-alert-red', arches.translations.requestFailed.title, response.responseJSON?.message);
                    if(self.updateRequest.statusText !== 'abort'){
                        self.alert(alert);
                    }
                    this.sharedStateObject.loading(false);
                },
                complete: function(request, status) {
                    self.updateRequest = undefined;
                    window.history.pushState({}, '', '?' + $.param(queryObj).split('+').join('%20'));
                    this.sharedStateObject.loading(false);
                }
            });
        },

        updateQuery: function() {
            let queryObj = this.query();
            queryObj[componentName] = true;
            this.query(queryObj);
        },

        restoreState: function(){
            if (!this.query()[componentName]) {
                this.updateQuery();
            } else {
                this.sharedStateObject.loading(false);
            }
        },

        clear: function(){ return; }
    });

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: coreSearchTemplate,
    });
});
