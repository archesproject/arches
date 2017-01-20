define([
    'jquery',
    'backbone',
    'knockout',
    'arches',
    'views/resource/related-resources-graph'
], function($, Backbone, ko, arches, RelatedResourcesGraph) {
    return Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.searchResults = options.searchResults;
            this.context = options.context;
            this.relationshipCandidates = ko.observableArray()
            this.showRelatedProperties = ko.observable(false);
            this.searchResults.showRelationships.subscribe(function(val){
                self.showRelatedResourcesGrid(val);
            })
            this.currentResource = {
                primaryname: ko.observable(),
                primarydescription: ko.observable(),
                resourceinstanceid: ko.observable()
            }
        },
        showRelatedResourcesGraph: function(e) {
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
        showRelatedResourcesGrid: function(resourceinstance) {
            this.currentResource.resourceinstanceid(resourceinstance.resourceinstanceid);
            this.currentResource.primaryname(resourceinstance.primaryname);
            this.currentResource.primarydescription(resourceinstance.primarydescription);
        },
        saveRelationships: function() {
            this.relationshipCandidates(_.pluck(this.searchResults.results(), 'resourceinstanceid'));
            this.currentResource.resourceinstanceid('c044cd5e-df16-11e6-abb6-c4b301baab9f');
            var target_resourceinstanceid = this.currentResource.resourceinstanceid();
            var instances_to_relate = this.relationshipCandidates();
            //TODO Create a resource_x_resource model rather than calling jQuery here
            var payload = {
                relationship_type: 'a9deade8-54c2-4683-8d76-a031c7301a47',
                instances_to_relate: instances_to_relate,
                target_resourceinstanceid: target_resourceinstanceid
            }
            $.ajax({
                url: arches.urls.related_resources,
                data: payload,
                type: 'POST',
                dataType: 'json'
            })
            .done(function(data) {
                console.log('success', data);
            })
            .fail(function(data){
                console.log('failed', data)
            });
        }
    });
});
