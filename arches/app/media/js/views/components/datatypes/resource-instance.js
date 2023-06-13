define([
    'knockout',
    'underscore',
    'arches',
    'view-data',
    'utils/ontology',
    'templates/views/components/datatypes/resource-instance.htm',
    'views/components/widgets/resource-instance-select',
    'bindings/key-events-click',
], function(ko, _, arches, data, ontologyUtils, resourceInstanceDatatypeTemplate) {
    var name = 'resource-instance-datatype-config';
    const viewModel = function(params) {
        var self = this;

        const defaultRelationshipCollection = '00000000-0000-0000-0000-000000000005';
        const defaultRelationshipConceptValue = 'ac41d9be-79db-4256-b368-2f4559cfbe55';
        this.search = params.search;
        this.resourceModels = [{
            graphid: null,
            name: ''
        }].concat(_.map(data.createableResources, function(graph) {
            return {
                graphid: graph.graphid,
                name: graph.name
            };
        }));
        if (!this.search) {
            this.makeFriendly = ontologyUtils.makeFriendly;
            this.getSelect2ConfigForOntologyProperties = ontologyUtils.getSelect2ConfigForOntologyProperties;
            this.isEditable = params.isEditable;
            this.graphIsSemantic = !!params.graph.get('ontology_id');
            this.rootOntologyClass = params.graph.get('root').ontologyclass();
            this.graphName = params.graph.get('root').name();
            if (params.graph) {
                var cards = _.filter(params.graph.get('cards')(), function(card){return card.nodegroup_id === params.nodeGroupId();});
                if (cards.length) {
                    this.isEditable = cards[0].is_editable;
                }
            } else if (params.widget) {
                this.isEditable = params.widget.card.get('is_editable');
            }
            
            this.node = params;
            this.config = params.config;
            this.openSearch = function(){
                window.open(self.config.searchString(), '_blank');
            };
            this.selectedResourceModel = ko.observable('');
            this.selectedResourceModel.subscribe(function(resourceType) {
                if (resourceType.length > 0) {
                    resourceType = resourceType.concat(self.config.graphs());
                    self.config.graphs(resourceType);
                    self.selectedResourceModel([]);
                }
            });

            this.selectedResourceType = ko.observable(null);
            this.toggleSelectedResource = function(resourceRelationship) {
                if (self.selectedResourceType() === resourceRelationship) {
                    self.selectedResourceType(null);
                } else {
                    self.selectedResourceType(resourceRelationship);
                }
            };

            var preventSetup = false;
            var setupConfig = function(graph) {
                var model = _.find(self.resourceModels, function(model){
                    return graph.graphid === model.graphid;
                });
                graph.ontologyProperty = ko.observable(ko.unwrap(graph.ontologyProperty));
                graph.inverseOntologyProperty = ko.observable(ko.unwrap(graph.inverseOntologyProperty));
                graph.relationshipCollection = ko.observable(ko.unwrap(graph.relationshipCollection) || defaultRelationshipCollection);
                graph.relationshipConcept = ko.observable(ko.unwrap(graph.relationshipConcept) || defaultRelationshipConceptValue);
                graph.inverseRelationshipConcept = ko.observable(ko.unwrap(graph.inverseRelationshipConcept || defaultRelationshipConceptValue));
                graph.useOntologyRelationship = ko.observable(ko.unwrap(graph.useOntologyRelationship || false));
                graph.removeRelationship = function(graph){
                    self.config.graphs.remove(graph);
                };
                graph.relationshipCollection.subscribe(()=>{
                    graph.relationshipConcept(null);
                    graph.inverseRelationshipConcept(null);
                });
                if(!!model){
                    // use this so that graph.name won't get saved back to the node config
                    Object.defineProperty(graph, 'name', {
                        value: model.name
                    });
                    window.fetch(arches.urls.graph_nodes(graph.graphid))
                        .then(function(response){
                            if(response.ok) {
                                return response.json();
                            }
                            throw("error");
                        })
                        .then(function(json) {
                            var node = _.find(json, function(node) {
                                return node.istopnode;
                            });
                            // use this so that graph.ontologyclass won't get saved back to the node config
                            Object.defineProperty(graph, 'ontologyClass', {
                                value: node.ontologyclass
                            });
                        });

                    // need to listen to these properties change so we can 
                    // trigger a "dirty" state in the config
                    var triggerDirtyState = function() {
                        preventSetup = true;
                        self.config.graphs(self.config.graphs());
                        preventSetup = false;
                    };
                    graph.ontologyProperty.subscribe(triggerDirtyState);
                    graph.inverseOntologyProperty.subscribe(triggerDirtyState);
                    graph.relationshipConcept.subscribe(triggerDirtyState);
                    graph.inverseRelationshipConcept.subscribe(triggerDirtyState);
                    graph.useOntologyRelationship.subscribe(triggerDirtyState);
                }else{
                    Object.defineProperty(graph, 'name', {
                        value: arches.translations.modelDoesNotExist
                    });
                }
            };

            this.config.graphs().forEach(function(graph) {
                setupConfig(graph);
            });

            // this should only get completely run when discarding edits
            this.config.graphs.subscribe(function(graphs){
                if (!preventSetup) {
                    graphs.forEach(function(graph) {
                        setupConfig(graph);
                    });
                }
            });

            this.config.searchString.subscribe(function(searchString){
                if(searchString !== ''){
                    var searchUrl = new URL(ko.unwrap(searchString));
                    var queryString = new URLSearchParams(searchUrl.search);
                    window.fetch(arches.urls.get_dsl + '?' + queryString.toString())
                        .then(function(response){
                            if(response.ok) {
                                return response.json();
                            }
                            throw("error");
                        })
                        .then(function(json) {
                            self.config.searchDsl(json.query);
                        });
                } else {
                    self.config.searchDsl('');
                }
            });

            this.formatLabel = function(name, ontologyProperty, inverseOntologyProperty){
                if (self.graphIsSemantic) {
                    return name + ' (' + ontologyUtils.makeFriendly(ontologyProperty) + '/' + ontologyUtils.makeFriendly(inverseOntologyProperty) + ')';
                }
                else {
                    return name;
                }
            };

        } else {
            var filter = params.filterValue();
            this.node = params.node;
            this.op = ko.observable(filter.op || '');
            this.searchValue = ko.observable(filter.val || '');
            this.filterValue = ko.computed(function() {
                return {
                    op: self.op(),
                    val: self.searchValue() || ''
                };
            }).extend({ throttle: 750 });
            params.filterValue(this.filterValue());
            this.filterValue.subscribe(function(val) {
                params.filterValue(val);
            });
            this.datatype = params.datatype;

        }
    };

    ko.components.register(name, {
        viewModel: viewModel,
        template: resourceInstanceDatatypeTemplate,
    });

    return name;
});
