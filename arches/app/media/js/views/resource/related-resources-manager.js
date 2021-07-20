define([
    'jquery',
    'underscore',
    'backbone',
    'knockout',
    'knockout-mapping',
    'arches',
    'views/components/widgets/resource-instance-multiselect',
    'views/resource/related-resources-node-list',
    'utils/ontology',
    'views/components/related-resources-graph',
    'plugins/knockout-select2',
    'bindings/datepicker',
    'bindings/datatable'
], function($, _, Backbone, ko, koMapping, arches, ResourceInstanceSelect, RelatedResourcesNodeList, ontologyUtils) {
    return ko.components.register('related-resources-manager', {
        viewModel: Backbone.View.extend({
            initialize: function(options) {
                var self = this;
                this.searchResults = options.searchResultsVm;
                this.editingInstanceId = options.editing_instance_id;
                this.graph = options.graph;
                this.loading = options.loading;
                this.rootOntologyClass  = '';
                this.activeTab = ko.observable();
                if (this.graph) {
                    if(!!options.graph.ontologyclass){
                        this.rootOntologyClass = options.graph.ontologyclass;
                    }else{
                        if(options.graph.root){
                            this.rootOntologyClass = options.graph.root.ontologyclass;
                        }
                    }
                }
                this.graphIsSemantic = !!this.rootOntologyClass;
                this.makeFriendly = ontologyUtils.makeFriendly;
                this.getSelect2ConfigForOntologyProperties = ontologyUtils.getSelect2ConfigForOntologyProperties;
                this.graphNameLookup = _.indexBy(arches.resources, 'graphid');
                this.currentResource = ko.observable();
                this.currentResourceSubscriptions = [];
                this.resourceEditorContext = options.resourceEditorContext;
                this.containerBottomMargin = ko.observable(0);
                this.showRelatedProperties = ko.observable(false);
                this.showGraph = ko.observable(this.editingInstanceId === undefined);
                this.displaySplash = ko.observable(false);
                this.graphNodeSelection = ko.observableArray();
                this.graphNodeList = ko.observableArray();
                this.newResource = ko.observableArray();
                this.filter = ko.observable('');
                this.selectedResourceRelationship = ko.observable();
                this.relationshipCandidates = ko.observableArray([]);
                this.relationshipCandidateIds = ko.observable([]);
                this.selectedOntologyClass = ko.observable();
                this.reportResourceId = ko.observable();
                this.reportGraphId = ko.observable(null);
                this.resourceRelationships = ko.observableArray();
                this.paginator = koMapping.fromJS({});
                this.totalRelationships = ko.observable(0);
                this.relationshipsInFilter = ko.computed(function() {
                    return self.resourceRelationships().filter(function(relationship) {
                        return self.filter().toLowerCase() === '' || relationship.resource.displayname.toLowerCase().includes(self.filter().toLowerCase());
                    });
                });

                this.toggleTab = function(tabName) {
                    if (self.activeTab() === tabName) {
                        self.activeTab(null);
                    } else {
                        self.activeTab(tabName);
                    }
                };

                this.toggleSelectedResourceRelationship = function(resourceRelationship) {
                    if (self.selectedResourceRelationship() === resourceRelationship) {
                        self.selectedResourceRelationship(null);
                    } else {
                        self.selectedResourceRelationship(resourceRelationship);
                    }
                };

                this.selectedResourceRelationship.subscribe(function(resourceRelationship) {
                    if (!!resourceRelationship) {
                        self.selectedOntologyClass(resourceRelationship.resource.root_ontology_class);
                    } else {
                        self.selectedOntologyClass(undefined);
                    }
                });

                this.selectedOntologyClass.subscribe(function() {
                    if (self.graphIsSemantic) {
                        self.relationshipTypes(self.validproperties[self.selectedOntologyClass()]);
                    } else {
                        self.relationshipTypes(options.relationship_types.values);
                    }
                });

                this.disableSearchResults = function(result) {
                    var resourceinstanceid = this.editingInstanceId;
                    var graph = this.graph;
                    if (result._id === resourceinstanceid || _.contains(graph.relatable_resources, result._source.graph_id) === false) {
                        return true;
                    } else {
                        return false;
                    }
                };

                this.selected = ko.computed(function() {
                    var res = _.filter(
                        self.resourceRelationships(),
                        function(rr) {
                            if (rr.selected() === true) {
                                return rr;
                            }
                        }, self);
                    if (self.graphIsSemantic && self.resourceEditorContext === true) {
                        if (res.length > 0 && self.graphIsSemantic) {
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

                this.dirty = ko.computed(function() {
                    return self.resourceRelationships().some(function(rr) {
                        return rr.dirty();
                    }, self);
                });


                this.newPage = function(page, e) {
                    if (page) {
                        this.currentResource().get(page);
                    }
                };

                var getNodeData = function(nodeid, relationship) {
                    $.ajax({
                        url: arches.urls.api_nodes(nodeid),
                        context: this,
                        dataType: 'json'
                    })
                        .done(function(data) {
                            relationship.node.name(data[0].name);
                            relationship.node.ontologyclass(data[0].ontologyclass);
                        })
                        .fail(function(data) {
                            console.log('Failed to get Node data', data);
                        });
                };

                this.createResource = function(resourceinstanceid) {
                    var self = this;
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
                                relationship = koMapping.fromJS(relationship);
                                relationship.node = {
                                    'name': ko.observable(),
                                    'ontologyclass': ko.observable()
                                };
                                relationship.reset = function() {
                                    koMapping.fromJS(JSON.parse(this._json()), relationship);
                                };
                                relationship._json = ko.observable(JSON.stringify(koMapping.toJS(relationship)));
                                relationship.dirty = ko.computed(function() {
                                    return JSON.stringify(koMapping.toJS(relationship)) !== relationship._json();
                                });
                                relationship.selected = ko.observable(false);
                                relationship.unselectable = ko.observable(false);
                                relationship.updateSelection = function(val) {
                                    return function(rr) {
                                        var vm = viewModel;
                                        if (!vm.graphIsSemantic) {
                                            rr.selected(!rr.selected());
                                        } else if (vm.graphIsSemantic && (vm.selectedOntologyClass() === rr.resource.root_ontology_class || !vm.selectedOntologyClass())) {
                                            rr.selected(!rr.selected());
                                        }
                                    };
                                };
                                if (!!relationship.nodeid()) {
                                    getNodeData(relationship.nodeid(), relationship);
                                }
                                relationship['resource'] = res.length > 0 ? res[0] : '';
                                if (!!relationship['resource']) {
                                    relationship.iconclass = viewModel.graphNameLookup[relationship.resource.graph_id].icon;
                                }
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
                            self.totalRelationships(rr.total.value);
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

                            if (!relationshipProperties.relationshiptype) {
                                relationshipProperties.relationshiptype = options.relationship_types.default;
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
                    if (!this.graphIsSemantic) {
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
                        datestarted: '',
                        dateended: '',
                        relationshiptype: undefined,
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
                    this.searchResults.relationshipCandidates.subscribe(function(val) {
                        if (val.length > 0) {
                            this.saveRelationships(val);
                        }
                    }, this);

                    this.searchResults.showRelationships.subscribe(function(val) {
                        this.currentResource(this.createResource(val.resourceinstanceid));
                        this.getRelatedResources();
                        this.currentResource().resourceRelationships.subscribe(function(val) {
                            this.resourceRelationships(val);
                        }, this);
                        this.currentResource().paging.subscribe(function(val) {
                            koMapping.fromJS(val, this.paginator);
                        }, this);
                    }, this);
                }

                var url = ko.observable(arches.urls.search_results);
                this.url = url;
                this.select2Config = {
                    placeholder: 'Search for resources',
                    value: this.relationshipCandidateIds,
                    clickBubble: true,
                    multiple: false,
                    closeOnSelect: true,
                    allowClear: true,
                    disabled: this.disabled,
                    ajax: {
                        url: function() {
                            return url();
                        },
                        dataType: 'json',
                        quietMillis: 250,
                        data: function(term, page) {
                            //TODO This regex isn't working, but it would nice fix it so that we can do more robust url checking
                            // var expression = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
                            // var regex = new RegExp(expression);
                            // var isUrl = val.target.value.match(regex)
                            var isUrl = term.startsWith('http');
                            if (isUrl) {
                                url(term.replace('search', 'search/resources'));
                                return {};
                            } else {
                                url(arches.urls.search_results);
                                var data = { 'paging-filter': page };
                                if (self.graph.relatable_resources.length > 0) {
                                    data['resource-type-filter'] = JSON.stringify(
                                        self.graph.relatable_resources.map(function(id) {
                                            return {
                                                "graphid": id,
                                                "inverted": false
                                            };
                                        })
                                    );
                                }
                                if (term) {
                                    data['term-filter'] = JSON.stringify([{
                                        "inverted": false,
                                        "type": "string",
                                        "context": "",
                                        "context_label": "",
                                        "id": term,
                                        "text": term,
                                        "value": term
                                    }]);
                                }
                                return data;
                            }
                        },

                        results: function(data, page) {
                            return {
                                results: data.results.hits.hits,
                                more: data['paging-filter'].paginator.has_next
                            };
                        }
                    },
                    onSelect: function(item) {
                        $.ajax(arches.urls.related_resource_candidates, {
                            dataType: 'json',
                            data: { resourceids: item._id }
                        }).done(function(data) {
                            self.relationshipCandidates(data);
                            self.saveRelationships();
                            self.relationshipCandidateIds(null);
                        });
                    },
                    id: function(item) {
                        return item._id;
                    },
                    formatResult: function(item) {
                        if (self.disableSearchResults(item) === false) {
                            if (item._source) {
                                return item._source.displayname;
                            } else {
                                return '<b> Create a new ' + item.name + ' . . . </b>';
                            }
                        } else {
                            return '<span>' + item._source.displayname + ' Cannot be related</span>';
                        }
                    },
                    formatResultCssClass: function(item) {
                        if (self.disableSearchResults(item) === false) {
                            return '';
                        } else {
                            return 'disabled';
                        }
                    },
                    formatSelection: function(item) {
                        if (item._source) {
                            return item._source.displayname;
                        } else {
                            return item.name;
                        }
                    },
                    initSelection: function(el, callback) { }
                };
            },

            deleteRelationships: function(relationship) {
                var resourcexids;
                var resource = this.currentResource();
                if (!!relationship) {
                    resourcexids = [relationship.resourcexid];
                } else {
                    resourcexids = _.pluck(this.selected(), 'resourcexid');
                }
                resource.delete(resourcexids);
            },

            saveRelationship: function(relationship) {
                var resource = this.currentResource();
                resource.save([], koMapping.toJS(relationship), [relationship.resourcexid()]);
            },

            saveRelationships: function() {
                var candidateIds = _.pluck(this.relationshipCandidates(), 'resourceinstanceid');
                var selectedResourceXids = _.pluck(this.selected(), 'resourcexid');
                var resource = this.currentResource();
                this.relationshipCandidates().forEach(function(rr) {
                    if (!this.relatedProperties.relationshiptype() && rr.ontologyclass && this.validproperties[rr.ontologyclass]) {
                        this.relatedProperties.relationshiptype(this.validproperties[rr.ontologyclass][0].id);
                    } else {
                        this.relatedProperties.relationshiptype(this.defaultRelationshipType);
                    }
                }, this);
                if (candidateIds.length > 0 || selectedResourceXids.length > 0) {
                    resource.save(candidateIds, koMapping.toJS(this.relatedProperties), selectedResourceXids);
                    if (candidateIds.length > 0) {
                        this.relationshipCandidates.removeAll();
                    }
                }
                this.relatedProperties.relationshiptype(undefined);
            },

            getRelatedResources: function() {
                var resource = this.currentResource();
                resource.get();
                this.resourceRelationships(resource.resourceRelationships());
            },

            updateTile: function(options, relationship) {
                var self = this;
                self.loading(true);
                window.fetch(arches.urls.api_tiles(relationship.tileid()), {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                    .then(function(response) {
                        if (response.ok) {
                            return response.json();
                        }
                    })
                    .then(function(tile) {
                        var newResourceRelations = [];
                        var tiledata = tile.data;
                        var resourceRelations = tiledata[relationship.nodeid()];
                        resourceRelations.forEach(function(relation) {
                            if (relation.resourceXresourceId === relationship.resourcexid()) {
                                relation.ontologyProperty = relationship.relationshiptype();
                                relation.inverseOntologyProperty = relationship.inverserelationshiptype();
                            } else {
                                newResourceRelations.push(relation);
                            }
                        });
                        if (!!options.delete) {
                            tiledata[relationship.nodeid()] = newResourceRelations;
                        }

                        window.fetch(arches.urls.api_tiles(relationship.tileid()), {
                            method: 'POST',
                            credentials: 'include',
                            body: JSON.stringify(tile),
                            headers: {
                                'Content-Type': 'application/json'
                            },
                        })
                            .then(function(response) {
                                if (response.ok) {
                                    relationship._json(JSON.stringify(koMapping.toJS(relationship)));
                                    if (!!options.delete) {
                                        window.setTimeout(function() {
                                            self.newPage(1);
                                            self.loading(false);
                                        }, 1000);
                                    }
                                }
                            })
                            .catch(function(err) {
                                console.log('Tile update failed', err);
                                self.loading(false);
                            });

                    })
                    .catch(function(err) {
                        console.log('Tile update failed', err);
                        self.loading(false);
                    });
            },
        }),
        template: { require: 'text!templates/views/resource/related-resources/related-resources-manager.htm' }
    });
});
