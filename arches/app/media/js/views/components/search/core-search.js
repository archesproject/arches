define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'viewmodels/alert',
    'templates/views/components/search/core-search.htm',
], function($, _, ko, arches, AlertViewModel, coreSearchTemplate) {
    const componentName = 'core-search';
    const viewModel = function(params) {
        const self = this;
        this.query = params.query;
        this.queryString = params.queryString;
        this.updateRequest = params.updateRequest;
        this.searchResults = params.searchResults;
        this.userIsReviewer = params.userIsReviewer;
        this.total = params.total;
        this.userid = params.userid;
        this.hits = params.hits;
        this.alert = params.alert;
        this.sharedStateObject = params;
        let localQueryObj = this.query();
        localQueryObj[componentName] = true;
        this.query(localQueryObj);
        this.queryString.subscribe(function() {
            this.doQuery();
        }, this);
        this.selectedPopup = ko.observable('');
        this.sharedStateObject.selectedPopup = this.selectedPopup;
        var firstEnabledFilter = _.find(this.sharedStateObject.filtersList, function(filter) {
            return filter.type === 'filter' && filter.enabled === true;
        }, this);
        this.selectedTab = ko.observable(firstEnabledFilter.componentname);
        this.sharedStateObject.selectedTab = this.selectedTab;

        this.filterApplied = ko.pureComputed(function(){
            var self = this;
            var filterNames = Object.keys(this.sharedStateObject.filters);
            return filterNames.some(function(filterName){
                if (ko.unwrap(self.sharedStateObject.filters[filterName]) && filterName !== 'paging-filter') {
                    return !!ko.unwrap(self.sharedStateObject.filters[filterName]).query()[filterName];
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
        this.sharedStateObject.toggleRelationshipCandidacy = this.toggleRelationshipCandidacy;

        this.clearQuery = function(){
            Object.values(this.sharedStateObject.filters).forEach(function(value){
                if (value()){
                    if (value().clear){
                        value().clear();
                    }
                }
            }, this);
            this.query({"paging-filter": "1", tiles: "true"});
        };

        this.selectPopup = function(componentname) {
            if(this.selectedPopup() !== '' && componentname === this.selectedPopup()) {
                this.selectedPopup('');
            } else {
                this.selectedPopup(componentname);
            }
        };

        this.doQuery = function() {
            let queryObj = JSON.parse(this.queryString());
            queryObj[componentName] = true;
            queryObj['localize-descriptors'] = true;

            if (self.updateRequest) {
                self.updateRequest.abort();
            }

            self.updateRequest = $.ajax({
                type: "GET",
                url: arches.urls.search_results,
                data: queryObj,
                context: this,
                success: function(response) {
                    _.each(self.searchResults, function(value, key, results) {
                        if (key !== 'timestamp') {
                            delete self.searchResults[key];
                        }
                    }, this);
                    _.each(response, function(value, key, response) {
                        if (key !== 'timestamp') {
                            self.searchResults[key] = value;
                        }
                    }, this);
                    self.searchResults.timestamp(response.timestamp);
                    self.userIsReviewer(response.reviewer);
                    self.userid(response.userid);
                    self.total(response.total_results);
                    self.hits(response.results.hits.hits.length);
                    self.alert(false);
                },
                error: function(response, status, error) {
                    const alert = new AlertViewModel('ep-alert-red', arches.translations.requestFailed.title, response.responseJSON?.message);
                    if(self.updateRequest.statusText !== 'abort'){
                        self.alert(alert);
                    }
                },
                complete: function(request, status) {
                    self.updateRequest = undefined;
                    window.history.pushState({}, '', '?' + $.param(queryObj).split('+').join('%20'));
                }
            });
        },

        updateQuery = function() {
            let queryObj = this.query();
            queryObj[componentName] = true;
            this.query(queryObj);
        },

        restoreState = function(){
            if (!this.query()[componentName]) {
                this.updateQuery();
            }
        }
    };

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: coreSearchTemplate,
    });
});
