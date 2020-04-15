define([
    'knockout',
    'underscore',
    'view-data',
    'arches',
    'views/components/widgets/resource-instance-select'
], function (ko, _, data, arches) {
    var name = 'resource-instance-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.resourceModels = [{
                graphid: null,
                name: ''
            }].concat(_.filter(data.createableResources, function (graph) {
                return graph;
            }));
            this.config = params.config;

            this.config.graphs().forEach(function(graph) {
                var model = _.find(self.resourceModels, function(model){
                    return graph.graphid === model.graphid;
                });
                graph.name = model.name;
                graph.ontologyProperty = ko.observable(graph.ontologyProperty);
                graph.inverseOntologyProperty = ko.observable(graph.inverseOntologyProperty);
                graph.editing = ko.observable(false);
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
                        graph.ontologyclass = node.ontologyclass;
                    });
            });

            this.node = params;

            this.search = params.search;
            if (!this.search) {
                this.isEditable = true;
                if (params.graph) {
                    var cards = _.filter(params.graph.get('cards')(), function(card){return card.nodegroup_id === params.nodeGroupId()})
                    if (cards.length) {
                        this.isEditable = cards[0].is_editable
                    }
                } else if (params.widget) {
                    this.isEditable = params.widget.card.get('is_editable')
                }
            } else {
                var filter = params.filterValue();
                this.node = params.node;
                this.op = ko.observable(filter.op || '');
                this.searchValue = ko.observable(filter.val || '');
                this.filterValue = ko.computed(function () {
                    return {
                        op: self.op(),
                        val: self.searchValue() || ''
                    }
                }).extend({ throttle: 750 });
                params.filterValue(this.filterValue());
                this.filterValue.subscribe(function (val) {
                    params.filterValue(val);
                });

            }

            this.makeFriendly = function(item) {
                if (!!item) {
                    var parts = item.split("/");
                    return parts[parts.length-1];
                }
                return '';
            };

            this.getSelect2ConfigForOntologyProperties = function(value, domain, range) {
                return {
                    value: value,
                    clickBubble: false,
                    placeholder: 'Select an Ontology Property',
                    closeOnSelect: true,
                    allowClear: false,
                    ajax: {
                        url: function() {
                            return arches.urls.ontology_properties;
                        },
                        data: function(term, page) {
                            var data = { 
                                'domain_ontology_class': domain,
                                'range_ontology_class': range,
                                'ontologyid': ''
                            };
                            return data;
                        },
                        dataType: 'json',
                        quietMillis: 250,
                        results: function(data, page) {
                            return {
                                results: data
                            };
                        }
                    },
                    id: function(item) {
                        return item;
                    },
                    formatResult: this.makeFriendly,
                    formatSelection: this.makeFriendly,
                    initSelection: function(el, callback) {
                        callback(value());
                    }
                };
            };
        },
        template: { require: 'text!datatype-config-templates/resource-instance' }
    });
    return name;
});
