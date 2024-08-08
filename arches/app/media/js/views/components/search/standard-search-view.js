define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'viewmodels/alert',
    'views/components/search/base-search-view',
    'templates/views/components/search/standard-search-view.htm',
], function($, _, ko, arches, AlertViewModel, BaseSearchViewComponent, standardSearchViewTemplate) {
    const componentName = 'standard-search-view';
    const viewModel = BaseSearchViewComponent.extend({ 
        initialize: function(sharedStateObject) {
            const self = this;
            sharedStateObject.componentName = componentName;
            BaseSearchViewComponent.prototype.initialize.call(this, sharedStateObject);
            this.defaultQuery = {"paging-filter": "1", "search-view":"standard-search-view", tiles: "true"};
            
            this.selectedPopup = ko.observable('');
            this.sharedStateObject.selectedPopup = this.selectedPopup;
            var firstEnabledFilter = _.find(this.sharedStateObject.filtersList, function(filter) {
                return filter.config.layoutType === 'tabbed';
            }, this);
            this.selectedTab = ko.observable(firstEnabledFilter.componentname);
            this.sharedStateObject.selectedTab = this.selectedTab;
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
            this.searchComponentVms[componentName](this);
        },

    });

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: standardSearchViewTemplate,
    });
});
