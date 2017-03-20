define([
    'jquery',
    'backbone',
    'knockout',
    'knockout-mapping',
    'arches',
    'bindings/related-resources-graph',
    'plugins/knockout-select2',
    'bindings/datepicker',
    'bindings/datatable'
], function($, Backbone, ko, koMapping, arches) {
    return Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.propertiesDialogOpen = ko.observable(false);
            this.searchResults = options.searchResults;
            this.editingInstanceId = options.editing_instance_id;
            this.currentResource = ko.observable();
            this.resourceEditorContext = options.resourceEditorContext;
            this.containerBottomMargin = ko.observable(700);
            this.showRelatedProperties = ko.observable(false);
            this.showGraph = ko.observable(false);

            _.each(this.relatedProperties, function(prop, key) {
                if (ko.isObservable(prop)) {
                    prop.subscribe(function(val) {
                        console.log(key, prop())
                    });
                };
            });
            this.searchResults.relationshipCandidates.subscribe(function(val) {
                if (val.length > 0) {
                    self.saveRelationships(val)
                }
            }, self);
            this.resourceRelationships = ko.observableArray();
            this.selected = ko.computed(function() {
                return _.filter(
                    this.resourceRelationships(),
                    function(rr) {
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
                        data.resource_relationships.forEach(function(relationship) {
                            var res = _.filter(resources, function(resource) {
                                if (_.contains([relationship.resourceinstanceidto, relationship.resourceinstanceidfrom], resource.resourceinstanceid)) {
                                    return resource;
                                }
                            });
                            relationship.selected = ko.observable(false);
                            relationship['resource'] = res.length > 0 ? res[0] : "";
                            relationshipsWithResource.push(relationship)
                        }, this)
                        var sorted = _(relationshipsWithResource).chain()
                            .sortBy(function(relate) {
                                return relate.resource.displayname;
                            })
                            .sortBy(function(relate) {
                                return relate.relationshiptype;
                            }).value();
                        this.resourceRelationships(sorted);
                        this.displayname = data.resource_instance.displayname;
                        this.graphid = data.resource_instance.graph_id;
                    },
                    get: function() {
                        $.ajax({
                                url: arches.urls.related_resources + resourceinstanceid,
                                context: this,
                                dataType: 'json'
                            })
                            .done(function(data) {
                                this.parse(data)
                            })
                            .fail(function(data) {
                                console.log('failed', data)
                            });
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
                            .done(function(data) {
                                this.parse(data)
                            })
                            .fail(function(data) {
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
                                url: arches.urls.related_resources + '?' + $.param(payload),
                                type: 'DELETE',
                                context: this,
                                dataType: 'json'
                            })
                            .done(function(data) {
                                this.parse(data)
                            })
                            .fail(function(data) {
                                console.log('failed', data)
                            });
                    }
                };
            };

            if (this.resourceEditorContext === true) {
                this.relationshipTypes = ko.observableArray(options.relationship_types.values);
                this.defaultRelationshipType = options.relationship_types.default;
                this.relationshipTypePlaceholder = ko.observable('Select a Relationship Type')
                this.relatedProperties = koMapping.fromJS({
                    datefrom: '',
                    dateto: '',
                    relationship_type: this.defaultRelationshipType,
                    notes: ''
                });

                this.currentResource(self.createResource(this.editingInstanceId));
                this.getRelatedResources();
                this.currentResource().resourceRelationships.subscribe(function(val) {
                    this.resourceRelationships(val);
                }, this)
            } else {
                this.searchResults.showRelationships.subscribe(function(val) {
                    self.currentResource(self.createResource(val.resourceinstanceid))
                    self.getRelatedResources();
                    self.currentResource().resourceRelationships.subscribe(function(val) {
                        self.resourceRelationships(val);
                    }, self)
                })
            }

            /**
            * Ensure that the container for the relation properties dropdown is tall enough to scroll to the bottom of the dropdown
            */
            this.resize = function(){
                var rrPropertiesHeight = $('#rr-properties-id').height()
                if (rrPropertiesHeight > 0) {
                    self.containerBottomMargin(rrPropertiesHeight * 0.3 + (self.selected().length * 20) + "px")
                }
            }

            this.propertiesDialogOpen.subscribe(function(val){
                if (val === true) {
                    setTimeout(this.resize, 1000);
                }
            }, this)

        },

        deleteRelationships: function() {
            var resource = this.currentResource();
            var resourcexids = _.pluck(this.selected(), 'resourcexid')
            resource.delete(resourcexids)
        },

        saveRelationships: function() {
            var candidateIds = _.pluck(this.searchResults.relationshipCandidates(), 'resourceinstanceid');
            var selectedResourceXids = _.pluck(this.selected(), 'resourcexid')
            var resource = this.currentResource()
            if (candidateIds.length > 0 || selectedResourceXids.length > 0) {
                resource.save(candidateIds, koMapping.toJS(this.relatedProperties), selectedResourceXids);
                if (candidateIds.length > 0) {
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
