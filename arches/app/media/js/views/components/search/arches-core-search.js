define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'viewmodels/alert',
    'views/components/search/base-core-search',
    'templates/views/components/search/arches-core-search.htm',
], function($, _, ko, arches, AlertViewModel, BaseCoreSearchComponent, archesCoreSearchTemplate) {
    const componentName = 'arches-core-search';
    const viewModel = BaseCoreSearchComponent.extend({ 
        initialize: function(sharedStateObject) {
            const self = this;
            sharedStateObject.componentName = componentName;
            BaseCoreSearchComponent.prototype.initialize.call(this, sharedStateObject);
            this.defaultQuery = {"paging-filter": "1", "core":"arches-core-search", tiles: "true"};
            
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

            this.selectPopup = function(componentname) {
                if(this.selectedPopup() !== '' && componentname === this.selectedPopup()) {
                    this.selectedPopup('');
                } else {
                    this.selectedPopup(componentname);
                }
            };
        },

    });

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: archesCoreSearchTemplate,
    });
});
