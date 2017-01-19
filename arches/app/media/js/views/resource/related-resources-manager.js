define([
    'jquery',
    'backbone',
    'knockout',
    'views/resource/related-resources-graph'
], function($, Backbone, ko, RelatedResourcesGraph) {
    return Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.searchResults = options.searchResults;
            this.context = options.context;
            this.addedSearchResults = ko.observableArray()
            this.showRelatedProperties = ko.observable(false);
            this.resources = ko.observableArray();
            this.searchResults.showRelationships.subscribe(function(val){
                self.showRelatedResourcesGrid(val);
            })
            this.currentResource = {
                primaryname: ko.observable(),
                primarydescription: ko.observable(),
                resourceinstanceid: ko.observable()
            }
        },
        showRelatedResourcesGraph: function (e) {
            var resourceId = $(e.target).data('resourceid');
            var primaryName = $(e.target).data('primaryname');
            var typeId = $(e.target).data('entitytypeid');
            var searchItem = $(e.target).closest('.arches-search-item');
            var graphPanel = searchItem.find('.arches-related-resource-panel');
            var nodeInfoPanel = graphPanel.find('.node_info');
            if (!graphPanel.hasClass('view-created')) {
                new RelatedResourcesGraph({
                    el: graphPanel[0],
                    resourceId: resourceId,
                    resourceName: primaryName,
                    resourceTypeId: typeId
                });
            }
            nodeInfoPanel.hide();
            $(e.target).closest('li').toggleClass('graph-active');
            graphPanel.slideToggle(500);
        },
        showRelatedResourcesGrid: function (resourceinstance) {
            this.currentResource.resourceinstanceid(resourceinstance.resourceinstanceid);
            this.currentResource.primaryname(resourceinstance.primaryname);
            this.currentResource.primarydescription(resourceinstance.primarydescription);
        }
    });
});
