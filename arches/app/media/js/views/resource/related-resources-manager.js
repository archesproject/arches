define([
    'jquery',
    'backbone',
    'knockout',
    'arches',
    'views/resource/related-resources-list'
], function($, Backbone, ko, arches, RelatedResourcesList) {
    return Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.searchResults = options.searchResults;
            this.editingInstanceId = options.editing_instance_id;
            this.context = options.context;
            this.showRelatedProperties = ko.observable(false);
            this.searchResults.relationshipCandidates.subscribe(function(changes) {
            }, null, "arrayChange");
            this.relatedresources = ko.observableArray()
            this.relationships = ko.observableArray()
            this.relatedresourceslist = new RelatedResourcesList({related:this.relatedresources, relationships:this.relationships});

            this.createResource = function(resourceinstanceid) {
                return {
                    resourceinstanceid: resourceinstanceid,
                    relatedresources: ko.observableArray(),
                    relationships: ko.observableArray(),
                    parse: function() {
                        var self = this;
                        return function(data) {
                            self.relatedresources(data.related_resources);
                            self.relationships(data.resource_relationships);
                        }
                    },
                    getRelatedResources: function() {
                        $.ajax({
                            url: arches.urls.related_resources + resourceinstanceid,
                            dataType: 'json'
                        })
                        .done(this.parse())
                        .fail(function(data){console.log('failed', data)});
                    },
                    saveRelationships: function(candidateIds) {
                        var self = this;
                        var payload = {
                            relationship_type: 'a9deade8-54c2-4683-8d76-a031c7301a47',
                            instances_to_relate: candidateIds,
                            root_resourceinstanceid: resourceinstanceid
                        }
                        $.ajax({
                            url: arches.urls.related_resources,
                            data: payload,
                            type: 'POST',
                            dataType: 'json'
                        })
                        .done(this.parse())
                        .fail(function(data){
                            console.log('failed', data)
                        });
                    },
                    deleteRelationships: function(relationshipIds) {
                        var self = this;
                        var payload = {
                            relationships: relationshipIds,
                            root_resourceinstanceid: resourceinstanceid
                        }
                        $.ajax({
                            url: arches.urls.related_resources,
                            data: payload,
                            type: 'DELETE',
                            dataType: 'json'
                        })
                        .done(this.parse())
                        .fail(function(data){
                            console.log('failed', data)
                        });
                    }
                };
            };

            this.currentResourceInstanceId = ko.observable(this.editingInstanceId)
            this.currentResource = ko.observable(self.createResource(this.editingInstanceId));
            this.searchResults.showRelationships.subscribe(function(val){
                self.currentResourceInstanceId(val.resourceinstanceid)
                self.showRelatedResourcesGrid(val);
            })

            this.currentResourceInstanceId.subscribe(function(val){
                self.currentResource(self.createResource(val))
            });

            if (this.editingInstanceId) {
                self.showRelatedResourcesGrid();
            }
        },

        saveRelationships: function(){
            var candidateIds = _.pluck(this.searchResults.relationshipCandidates(), 'resourceinstanceid');
            var resource = this.currentResource()
            resource.saveRelationships(candidateIds);
            this.searchResults.relationshipCandidates.removeAll()
        },

        deleteRelationships: function(){
            var resource = this.currentResource();
            console.log(this.resourceRelationships)
            resource.getRelatedResources();
        },

        showRelatedResourcesGrid: function(resourceinstance) {
            var resource = this.currentResource();
            var relatedresourceslist = ko.observable();
            resource.getRelatedResources();
            resource.relationships.subscribe(function(val){
                this.relationships(val);
            }, this)
        }
    });
});
