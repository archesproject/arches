define([
    'jquery',
    'backbone',
    'knockout',
    'knockout-mapping',
    'arches',
    'views/resource/related-resources-list',
    'bindings/datepicker',
    'bindings/summernote',
], function($, Backbone, ko, koMapping, arches, RelatedResourcesList, datepicker) {
    return Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.propertiesDialogOpen = ko.observable(false);
            this.searchResults = options.searchResults;
            this.editingInstanceId = options.editing_instance_id;
            this.currentResource = ko.observable();
            this.context = options.context;
            this.showRelatedProperties = ko.observable(false);
            this.relatedProperties = koMapping.fromJS({
                datefrom: '',
                dateto: '',
                relationship_type: 'a9deade8-54c2-4683-8d76-a031c7301a47',
                notes: ''
            });
            _.each(this.relatedProperties, function(prop, key){
                if (ko.isObservable(prop)) {
                    prop.subscribe(function(val){console.log(key, prop())});
                };
            });
            this.searchResults.relationshipCandidates.subscribe(function(val) {
               if (val.length > 0) {
                   self.saveRelationships(val)
               }
           }, self);
            this.resourceRelationships = ko.observableArray();
            this.relatedresourceslist = new RelatedResourcesList({relationships:this.resourceRelationships});
            this.selected = ko.computed(function(){
                return _.filter(
                    this.resourceRelationships(), function(rr){
                    if (rr.selected() === true) {
                        return rr
                    }
                }, this);
            }, this);

            this.createResource = function(resourceinstanceid) {
                return {
                    resourceinstanceid: resourceinstanceid,
                    relatedresources: ko.observableArray(),
                    relationships: ko.observableArray(),
                    resourceRelationships: ko.observableArray(),
                    parse: function(data) {
                            var relationshipsWithResource = [];
                            var resources = data.related_resources;
                            data.resource_relationships.forEach(function(relationship){
                                var res = _.filter(resources, function(resource){
                                    if (_.contains([relationship.resourceinstanceidto, relationship.resourceinstanceidfrom], resource.resourceinstanceid)){
                                        return resource;
                                    }
                                });
                                relationship['resource'] = res.length > 0 ? res[0] : "";
                                relationshipsWithResource.push(relationship)
                            }, this)
                            var sorted = _(relationshipsWithResource).chain()
                                .sortBy(function(relate) {
                                    return relate.resource.primaryname;
                                })
                                .sortBy(function(relate) {
                                    return relate.relationshiptype;
                                }).value();
                            self.resourceRelationships(sorted);
                    },
                    get: function() {
                        $.ajax({
                            url: arches.urls.related_resources + resourceinstanceid,
                            context: this,
                            dataType: 'json'
                        })
                        .done(function(data){this.parse(data)})
                        .fail(function(data){console.log('failed', data)});
                    },
                    save: function(candidateIds, relationshipProperties, relationshipIds) {
                        var root_resourceinstanceid = resourceinstanceid;
                        var self = this;
                        var payload = {
                            relationship_properties: relationshipProperties,
                            instances_to_relate: candidateIds,
                            root_resourceinstanceid: resourceinstanceid,
                            relationship_ids: relationshipIds
                        }
                        $.ajax({
                            url: arches.urls.related_resources,
                            data: payload,
                            context: this,
                            type: 'POST',
                            dataType: 'json'
                        })
                        .done(function(data){this.parse(data)})
                        .fail(function(data){
                            console.log('failed', data)
                        });
                    },
                    delete: function(relationshipIds) {
                        var self = this;
                        var payload = {
                            resourcexids: relationshipIds,
                            root_resourceinstanceid: resourceinstanceid
                        }
                        $.ajax({
                            url: arches.urls.related_resources +  '?' + $.param(payload),
                            type: 'DELETE',
                            context: this,
                            dataType: 'json'
                        })
                        .done(function(data){this.parse(data)})
                        .fail(function(data){
                            console.log('failed', data)
                        });
                    }
                };
            };

            if (this.context == 'resource-editor') {
                this.currentResource(self.createResource(this.editingInstanceId));
                this.getRelatedResources();
                this.currentResource().resourceRelationships.subscribe(function(val){
                    this.resourceRelationships(val);
                }, this)
            } else {
                this.searchResults.showRelationships.subscribe(function(val){
                    self.currentResource(self.createResource(val.resourceinstanceid))
                    self.getRelatedResources();
                    self.currentResource().resourceRelationships.subscribe(function(val){
                        self.resourceRelationships(val);
                    }, self)
                })
            }
        },

        deleteRelationships: function(){
            var resource = this.currentResource();
            var resourcexids = _.pluck(this.selected(), 'resourcexid')
            resource.delete(resourcexids)
        },

        saveRelationships: function(){
            var candidateIds = _.pluck(this.searchResults.relationshipCandidates(), 'resourceinstanceid');
            var selectedResourceXids = _.pluck(this.selected(), 'resourcexid')
            var resource = this.currentResource()
            if (candidateIds.length > 0 || selectedResourceXids.length > 0) {
                resource.save(candidateIds, koMapping.toJS(this.relatedProperties), selectedResourceXids);
                if (candidateIds.length > 0 ) {
                    this.searchResults.relationshipCandidates.removeAll()
                }
                this.propertiesDialogOpen(false);
            }
        },

        getRelatedResources: function(resourceinstance) {
            var resource = this.currentResource();
            resource.get();
            this.resourceRelationships(resource.resourceRelationships());
        }
    });
});
