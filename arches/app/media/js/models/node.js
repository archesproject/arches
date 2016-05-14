define([
    'knockout',
    'models/abstract',
    'arches'
], function (ko, AbstractModel, arches) {
    return AbstractModel.extend({
        url: arches.urls.node,

        initialize: function (options) {
            var self = this;
            self.graph = options.graph;
            self.datatypelookup = options.datatypelookup;

            self._node = ko.observable('');
            self.selected = ko.observable(false);
            self.filtered = ko.observable(false);
            self.name = ko.observable('');
            self.nodeGroupId = ko.observable('');
            self.datatype = ko.observable('');
            self.cardinality = ko.observable('n');
            self.validations = ko.observableArray();
            self.ontologyclass_id = ko.observable('');
            self.parentproperty_id = ko.observable('');
            self.ontology_cache = ko.observableArray();

            self.validclasses = ko.computed(function() {
                if (!self.parentproperty_id()) {
                    return _.chain(self.ontology_cache())
                        .sortBy(function(item){
                            return item.class.value;
                        })
                        .uniq(function(item){
                            return item.class.id;
                        })
                        .pluck('class')
                        .value();
                }else{
                    return _.chain(self.ontology_cache())
                        .sortBy(function(item){
                            return item.class.value;
                        })
                        .filter(function(item){
                            return item.property.id === self.parentproperty_id();
                        })
                        .pluck('class')
                        .value();
                }
            }, this),
            self.validproperties = ko.computed(function() {
                if (!self.ontologyclass_id()) {
                    return _.chain(self.ontology_cache())
                        .sortBy(function(item){
                            return item.property.value;
                        })
                        .uniq(function(item){
                            return item.property.id;
                        })
                        .pluck('property')
                        .value();
                }else{
                    return _.chain(self.ontology_cache())
                        .sortBy(function(item){
                            return item.property.value;
                        })
                        .filter(function(item){
                            return item.class.id === self.ontologyclass_id();
                        })
                        .pluck('property')
                        .value();
                }
            }, this);        

            self.parse(options.source);

            self.iconclass = ko.computed(function() {
                return self.datatypelookup[self.datatype()];
            });

            self.json = ko.computed(function() {
                return JSON.stringify(_.extend(JSON.parse(self._node()), {
                    name: self.name(),
                    datatype: self.datatype(),
                    nodegroup_id: self.nodeGroupId(),
                    cardinality: self.cardinality(),
                    validations: self.validations(),
                    ontologyclass_id: self.ontologyclass_id(),
                    parentproperty_id: self.parentproperty_id()
                }))
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._node();
            });

            self.isCollector = ko.computed(function () {
                return self.nodeid === self.nodeGroupId();
            });

            self.selected.subscribe(function(selected){
                if (selected){
                    self.getValidNodesEdges();
                }
            })
        },

        parse: function(source) {
            var self = this;
            self._node(JSON.stringify(source));
            self.name(source.name);
            self.nodeGroupId(source.nodegroup_id);
            self.datatype(source.datatype);
            self.cardinality(source.cardinality);
            self.ontologyclass_id(source.ontologyclass_id);
            self.parentproperty_id(source.parentproperty_id);
            self.validations.removeAll();
            source.validations.forEach(function(validation) {
                self.validations.push(validation);
            });

            self.parentproperty_value = source.parentproperty_value;
            self.ontologyclass_value = source.ontologyclass_value;

            self.nodeid = source.nodeid;
            self.istopnode = source.istopnode;

            self.set('id', self.nodeid);
        },

        reset: function () {
            this.parse(JSON.parse(this._node()), self);
        },

        toJSON: function () {
            return JSON.parse(this.json());
        },

        toggleIsCollector: function () {
            var nodeGroupId = this.nodeid;
            if (this.isCollector()) {
                var _node = JSON.parse(this._node());
                nodeGroupId = (this.nodeid === _node.nodegroup_id) ? null : _node.nodegroup_id;
            }
            this.nodeGroupId(nodeGroupId);
        },

        toggleCardinality: function () {
            var cardinality = (this.cardinality()==='n')?'1':'n';
            this.cardinality(cardinality);
        },

        getValidNodesEdges: function(){
            var relatedNodesEdges = this.getRelatedNodesEdges(this);
            // this.ontology_cache.removeAll();
            // this.ontology_cache.push({
            //     'property': {'id':this.parentproperty_id(),'value': this.parentproperty_value},
            //     'class': {'id':this.ontologyclass_id(),'value': this.ontologyclass_value}
            // })
            this._doRequest({
                type: "POST",
                url: this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','') + 'get_related_nodes',
                data: JSON.stringify(relatedNodesEdges)
            }, function(response, status, self){
                self.ontology_cache.removeAll();
                response.responseJSON.forEach(function(item){
                    item.ontology_classes.forEach(function(ontologyclass){
                        self.ontology_cache.push({
                            'property': item.ontology_property,
                            'class': ontologyclass
                        })
                    });
                }, this);
            }, this, 'changed');
        },

        getRelatedNodesEdges: function(){
            var ret = {
                'childedges': [],
                'parentnode': {}
            }
            this.graph.get('edges')().forEach(function (edge) {
                if (edge.rangenode_id === this.nodeid){
                    this.graph.get('nodes')().forEach(function (node) {
                        if (node.nodeid === edge.domainnode_id){
                            ret.parentnode = node;
                        }
                    });
                }
                if (edge.domainnode_id === this.nodeid){
                    ret.childedges.push(edge);
                }
            }, this);
            return ret
        },
    });
});
