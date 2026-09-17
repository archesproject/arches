import ko from 'knockout';
import _ from 'underscore';
import arches from 'arches';
import data from 'view-data';
import ontologyUtils from 'utils/ontology';
import controlledListUtils from 'utils/controlled-list';
import resourceInstanceDatatypeTemplate from 'templates/views/components/datatypes/resource-instance.htm';
import 'views/components/widgets/resource-instance-select';
import 'bindings/key-events-click';


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
        this.getSelect2ConfigForControlledListItems = controlledListUtils.getSelect2ConfigForControlledListItems;
        this.graphIsSemantic = !!params.graph.get('ontology_id');
        this.rootOntologyClass = params.graph.get('root').ontologyclass();
        this.graphName = params.graph.get('root').name();
        
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

        this.controlledListsAvailable = controlledListUtils.isAvailable();
        this.controlledLists = ko.observableArray();
        if (this.controlledListsAvailable) {
            controlledListUtils.getControlledLists()
                .then(function(lists) {
                    self.controlledLists(lists);
                })
                .catch(function() {
                    self.controlledLists([]);
                });
        }

        this.relationshipSources = [];
        if (this.graphIsSemantic) {
            this.relationshipSources.push({
                id: 'ontology-property',
                text: arches.translations.ontologyPropertySource
            });
        }
        this.relationshipSources.push({
            id: 'concept',
            text: arches.translations.conceptSource
        });
        if (this.controlledListsAvailable) {
            this.relationshipSources.push({
                id: 'reference',
                text: arches.translations.referenceSource
            });
        }

        this.selectedResourceType = ko.observable(null);
        this.toggleSelectedResource = function(resourceRelationship) {
            if (self.selectedResourceType() === resourceRelationship) {
                self.selectedResourceType(null);
            } else {
                self.selectedResourceType(resourceRelationship);
            }
        };

        const defaultRelationship = function(graph) {
            return graph.relationshipSource() === 'concept' ? defaultRelationshipConceptValue : null;
        };

        const clearRelationships = function(graph) {
            return function() {
                graph.relationship(null);
                graph.inverseRelationship(null);
            };
        };

        var preventSetup = false;
        var setupConfig = function(graph) {
            var model = _.find(self.resourceModels, function(model){
                return graph.graphid === model.graphid;
            });
            // configs saved before relationshipSource was introduced still carry the
            // legacy keys; read them once, then drop them so they aren't saved again
            const useOntologyRelationship = ko.unwrap(graph.useOntologyRelationship);
            const legacyRelationship = useOntologyRelationship ? graph.ontologyProperty : graph.relationshipConcept;
            const legacyInverseRelationship = useOntologyRelationship ? graph.inverseOntologyProperty : graph.inverseRelationshipConcept;

            graph.relationshipSource = ko.observable(
                ko.unwrap(graph.relationshipSource) || (useOntologyRelationship ? 'ontology-property' : 'concept')
            );
            graph.relationshipCollection = ko.observable(ko.unwrap(graph.relationshipCollection) || defaultRelationshipCollection);
            graph.relationshipControlledList = ko.observable(ko.unwrap(graph.relationshipControlledList) || null);
            graph.relationship = ko.observable(ko.unwrap(graph.relationship) ?? ko.unwrap(legacyRelationship) ?? defaultRelationship(graph));
            graph.inverseRelationship = ko.observable(ko.unwrap(graph.inverseRelationship) ?? ko.unwrap(legacyInverseRelationship) ?? defaultRelationship(graph));

            delete graph.useOntologyRelationship;
            delete graph.ontologyProperty;
            delete graph.inverseOntologyProperty;
            delete graph.relationshipConcept;
            delete graph.inverseRelationshipConcept;

            graph.removeRelationship = function(graph){
                self.config.graphs.remove(graph);
            };
            // the available relationships depend on the source and on the collection or
            // list they are drawn from, so clear the selections whenever those change
            graph.relationshipSource.subscribe(clearRelationships(graph));
            graph.relationshipCollection.subscribe(clearRelationships(graph));
            graph.relationshipControlledList.subscribe(clearRelationships(graph));
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
                graph.relationship.subscribe(triggerDirtyState);
                graph.inverseRelationship.subscribe(triggerDirtyState);
                graph.relationshipSource.subscribe(triggerDirtyState);
                graph.relationshipCollection.subscribe(triggerDirtyState);
                graph.relationshipControlledList.subscribe(triggerDirtyState);
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

export default name;
