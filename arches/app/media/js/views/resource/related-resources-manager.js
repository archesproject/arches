define([
    'jquery',
    'underscore',
    'backbone',
    'knockout',
    'knockout-mapping',
    'arches',
    'views/components/widgets/resource-instance-multiselect',
    'views/resource/related-resources-node-list',
    'bindings/related-resources-graph',
    'plugins/knockout-select2',
    'bindings/datepicker',
    'bindings/datatable'
], function($, _, Backbone, ko, koMapping, arches, ResourceInstanceSelect, RelatedResourcesNodeList) {
    return Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.propertiesDialogOpen = ko.observable(false);
            this.searchResults = options.searchResults;
            this.editingInstanceId = options.editing_instance_id;
            this.graph = options.graph;
            if (this.graph) {
                this.ontologyclass = options.graph.ontologyclass || options.graph.root.ontologyclass;
            }
            this.graphNameLookup = _.indexBy(arches.resources, 'graphid');
            this.currentResource = ko.observable();
            this.currentResourceSubscriptions = [];
            this.resourceEditorContext = options.resourceEditorContext;
            this.containerBottomMargin = ko.observable(700);
            this.showRelatedProperties = ko.observable(false);
            this.showGraph = ko.observable(this.editingInstanceId === undefined);
            this.displaySplash = ko.observable(false);
            this.graphNodeSelection = ko.observableArray();
            this.graphNodeList = ko.observableArray();
            this.newResource = ko.observableArray();
            this.fdgNodeListView = new RelatedResourcesNodeList({
                items: self.graphNodeList
            });

            this.disableSearchResults = function() {
                var resourceinstanceid = this.editingInstanceId;
                var graph = this.graph;
                return function(result) {
                    if (result._id === resourceinstanceid || _.contains(graph.relatable_resources, result._type) === false) {
                        return true;
                    } else {
                        return false;
                    }
                };
            };

            this.relationshipCandidates = ko.observableArray([]);
            this.relationshipCandidateIds = ko.observable([]);
            this.useSemanticRelationships = arches.useSemanticRelationships;
            this.selectedOntologyClass = ko.observable();
            this.resourceRelationships = ko.observableArray();
            this.paginator = koMapping.fromJS({});

            this.relateResources = function() {
                var self = this;
                $.ajax(arches.urls.related_resource_candidates, {
                    dataType: 'json',
                    data: {resourceids: JSON.stringify(this.relationshipCandidateIds())}
                }).done(function(data) {
                    self.relationshipCandidates(data);
                    self.saveRelationships();
                    self.relationshipCandidateIds(undefined);
                });
            };

            this.selectedOntologyClass.subscribe(function() {
                if (self.selectedOntologyClass() && self.validproperties[self.selectedOntologyClass()] !== undefined) {
                    self.relationshipTypes(self.validproperties[self.selectedOntologyClass()]);
                } else {
                    self.relationshipTypes(options.relationship_types.values);
                }
            });

            this.showGraph.subscribe(function(val) {
                this.graphNodeList([]);
            }, this);

            this.panelPosition = ko.computed(function() {
                var res = {x: 0, y: 0, first: [0, 0], second: [0, 0]};
                var nodes = self.graphNodeSelection();
                if (nodes.length === 2) {
                    res.x = nodes[0].absX < nodes[1].absX ? nodes[0].absX : nodes[1].absX;
                    res.y = nodes[0].absY < nodes[1].absY ? nodes[0].absY : nodes[1].absY;
                    res.first = nodes[0];
                    res.second = nodes[1];
                }
                return res;
            });

            if (!this.useSemanticRelationships) {
                this.columnConfig = [{
                    width: '20px',
                    orderable: true,
                    className: 'data-table-selected'
                }, {
                    width: '100px'
                }, {
                    width: '100px'
                }, {
                    width: '100px'
                }, {
                    width: '100px'
                }, {
                    width: '100px'
                }];
            } else {
                this.columnConfig = [{
                    width: '20px',
                    orderable: true,
                    className: 'data-table-selected'
                }, {
                    width: '100px'
                }, {
                    width: '100px'
                }, {
                    width: '100px'
                }];
            }

            this.searchResults.relationshipCandidates.subscribe(function(val) {
                if (val.length > 0) {
                    self.saveRelationships(val);
                }
            }, self);

            this.selected = ko.computed(function() {
                var res = _.filter(
                    self.resourceRelationships(),
                    function(rr) {
                        if (rr.selected() === true) {
                            return rr;
                        }
                    }, self);
                if (self.useSemanticRelationships && self.resourceEditorContext === true) {
                    // if (res.length > 0 && self.useSemanticRelationships && self.graph.root.ontologyclass) {
                    if (res.length > 0 && self.useSemanticRelationships && self.ontologyclass) {
                        self.selectedOntologyClass(res[0].resource.root_ontology_class);
                        self.resourceRelationships().forEach(function(rr) {
                            if (rr.resource.root_ontology_class !== self.selectedOntologyClass()) {
                                rr.unselectable(true);
                            }
                        });
                    } else {
                        self.selectedOntologyClass(undefined);
                        self.resourceRelationships().forEach(function(rr) {
                            rr.unselectable(false);
                        });
                    }
                }
                return res;
            });

            this.newPage = function(page, e) {
                if (page) {
                    this.currentResource().get(page);
                };
            };

            this.createResource = function(resourceinstanceid) {
                return {
                    resourceinstanceid: resourceinstanceid,
                    relatedresources: ko.observableArray(),
                    relationships: ko.observableArray(),
                    resourceRelationships: ko.observableArray(),
                    paging: ko.observable(),
                    parse: function(data, viewModel) {
                        var rr = data.related_resources;
                        var relationshipsWithResource = [];
                        var resources = rr.related_resources;
                        rr.resource_relationships.forEach(function(relationship) {
                            var res = _.filter(resources, function(resource) {
                                if (_.contains([relationship.resourceinstanceidto, relationship.resourceinstanceidfrom], resource.resourceinstanceid)) {
                                    return resource;
                                }
                            });
                            relationship.selected = ko.observable(false);
                            relationship.unselectable = ko.observable(false);
                            relationship.updateSelection = function(val) {
                                return function(rr) {
                                    var vm = viewModel;
                                    if (!vm.useSemanticRelationships) {
                                        rr.selected(!rr.selected());
                                    } else if (vm.useSemanticRelationships && (vm.selectedOntologyClass() === rr.resource.root_ontology_class || !vm.selectedOntologyClass())) {
                                        rr.selected(!rr.selected());
                                    };
                                };
                            };
                            relationship['resource'] = res.length > 0 ? res[0] : '';
                            relationship.iconclass = viewModel.graphNameLookup[relationship.resource.graph_id].icon;
                            relationshipsWithResource.push(relationship);
                        }, this);
                        var sorted = _(relationshipsWithResource).chain()
                            .sortBy(function(relate) {
                                return relate.created;
                            }).value().reverse();
                        this.paging(data.paginator);
                        this.resourceRelationships(sorted);
                        this.displayname = rr.resource_instance.displayname;
                        this.graphid = rr.resource_instance.graph_id;
                    },
                    get: function(newPage) {
                        var page = newPage || 1;
                        $.ajax({
                            url: arches.urls.related_resources + resourceinstanceid,
                            context: this,
                            dataType: 'json',
                            data: {
                                page: page
                            }
                        })
                            .done(function(data) {
                                self.graphNameLookup = _.indexBy(arches.resources, 'graphid');
                                this.parse(data, self);
                                self.newResource(this);
                            })
                            .fail(function(data) {
                                console.log('Related resource request failed', data);
                            });
                    },
                    save: function(candidateIds, relationshipProperties, relationshipIds) {
                        this.defaultRelationshipType = options.relationship_types.default;

                        if (!relationshipProperties.relationship_type) {
                            relationshipProperties.relationship_type = options.relationship_types.default;
                        }
                        var payload = {
                            relationship_properties: relationshipProperties,
                            instances_to_relate: candidateIds,
                            root_resourceinstanceid: resourceinstanceid,
                            relationship_ids: relationshipIds
                        };
                        $.ajax({
                            url: arches.urls.related_resources,
                            data: payload,
                            context: this,
                            type: 'POST',
                            dataType: 'json'
                        })
                            .done(function(data) {
                                this.parse(data, self);
                            })
                            .fail(function(data) {
                                console.log('Related resource request failed', data);
                            });
                    },
                    delete: function(relationshipIds) {
                        var payload = {
                            resourcexids: relationshipIds,
                            root_resourceinstanceid: resourceinstanceid
                        };
                        $.ajax({
                            url: arches.urls.related_resources + '?' + $.param(payload),
                            type: 'DELETE',
                            context: this,
                            dataType: 'json'
                        })
                            .done(function(data) {
                                this.parse(data, self);
                            })
                            .fail(function(data) {
                                console.log('Related resource request failed', data);
                            });
                    }
                };
            };

            if (this.resourceEditorContext === true) {
                this.relationshipTypes = ko.observableArray();
                if (!this.useSemanticRelationships || !this.ontologyclass) {
                    this.relationshipTypes(options.relationship_types.values);
                }

                this.validproperties = {};
                this.graph.domain_connections.forEach(function(item) {
                    item.ontology_classes.forEach(function(ontologyclass) {
                        if (!this.validproperties[ontologyclass]) {
                            this.validproperties[ontologyclass] = [];
                        } else {
                            this.validproperties[ontologyclass].push({
                                id: item.ontology_property,
                                text: item.ontology_property
                            });
                        }
                    }, this);
                }, this);

                _.each(this.validproperties, function(ontologyClass) {
                    ontologyClass.sort(function(a, b) {
                        if (a.id > b.id) {
                            return 1;
                        } else {
                            return -1;
                        }
                    });
                });

                this.relationshipTypePlaceholder = ko.observable('Select a Relationship Type');
                this.relatedProperties = koMapping.fromJS({
                    datefrom: '',
                    dateto: '',
                    relationship_type: undefined,
                    notes: ''
                });

                this.currentResource(self.createResource(this.editingInstanceId));
                this.getRelatedResources();
                this.currentResource().resourceRelationships.subscribe(function(val) {
                    this.resourceRelationships(val);
                    if (val.length === 0) {
                        this.displaySplash(true);
                    }
                }, this);
                this.currentResource().paging.subscribe(function(val) {
                    koMapping.fromJS(val, this.paginator);
                }, this);
            } else {
                this.searchResults.showRelationships.subscribe(function(val) {
                    self.currentResource(self.createResource(val.resourceinstanceid));
                    self.getRelatedResources();
                    self.currentResource().resourceRelationships.subscribe(function(val) {
                        self.resourceRelationships(val);
                    }, self);
                    self.currentResource().paging.subscribe(function(val) {
                        koMapping.fromJS(val, self.paginator);
                    }, self);
                });
            }

            /**
             * Ensure that the container for the relation properties dropdown is tall enough to scroll to the bottom of the dropdown
             */
            this.resize = function() {
                var rrPropertiesHeight = $('#rr-properties-id').height();
                if (rrPropertiesHeight > 0) {
                    self.containerBottomMargin(rrPropertiesHeight * 0.3 + (self.selected().length * 20) + 'px');
                }
            };

            this.propertiesDialogOpen.subscribe(function(val) {
                if (val === true) {
                    setTimeout(this.resize, 1000);
                } else {
                    this.relatedProperties.notes('');
                    this.relatedProperties.dateto('');
                    this.relatedProperties.datefrom('');
                    this.relatedProperties.relationship_type(this.defaultRelationshipType);
                }
            }, this);
        },

        deleteRelationships: function() {
            var resource = this.currentResource();
            var resourcexids = _.pluck(this.selected(), 'resourcexid');
            resource.delete(resourcexids);
        },

        saveRelationships: function() {
            var candidateIds = _.pluck(this.relationshipCandidates(), 'resourceinstanceid');
            var selectedResourceXids = _.pluck(this.selected(), 'resourcexid');
            var resource = this.currentResource();
            this.relationshipCandidates().forEach(function(rr) {
                if (!this.relatedProperties.relationship_type() && rr.ontologyclass && this.validproperties[rr.ontologyclass]) {
                    this.relatedProperties.relationship_type(this.validproperties[rr.ontologyclass][0].id);
                } else {
                    this.relatedProperties.relationship_type(this.defaultRelationshipType);
                }
            }, this);
            if (candidateIds.length > 0 || selectedResourceXids.length > 0) {
                resource.save(candidateIds, koMapping.toJS(this.relatedProperties), selectedResourceXids);
                if (candidateIds.length > 0) {
                    this.relationshipCandidates.removeAll();
                }
                this.propertiesDialogOpen(false);
            };
            this.relatedProperties.relationship_type(undefined);
        },

        getRelatedResources: function(resourceinstance) {
            var resource = this.currentResource();
            resource.get();
            this.resourceRelationships(resource.resourceRelationships());
        }
    });
});
