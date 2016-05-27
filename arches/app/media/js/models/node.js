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
            self.validations = ko.observableArray();
            self.ontologyclass = ko.observable('');
            self.parentproperty = ko.observable('');
            self.ontology_cache = ko.observableArray();

            self.parse(options.source);

            self.validclasses = ko.computed(function() {
                if (!self.parentproperty()) {
                    return _.chain(self.ontology_cache())
                        .sortBy(function(item){
                            return item.class;
                        })
                        .uniq(function(item){
                            return item.class;
                        })
                        .pluck('class')
                        .value();
                }else{
                    return _.chain(self.ontology_cache())
                        .sortBy(function(item){
                            return item.class;
                        })
                        .filter(function(item){
                            return item.property === self.parentproperty();
                        })
                        .pluck('class')
                        .value();
                }
            }, this);

            if(!self.istopnode){
                self.validproperties = ko.computed(function() {
                    if (!self.ontologyclass()) {
                        return _.chain(self.ontology_cache())
                            .sortBy(function(item){
                                return item.property;
                            })
                            .uniq(function(item){
                                return item.property;
                            })
                            .pluck('property')
                            .value();
                    }else{
                        return _.chain(self.ontology_cache())
                            .sortBy(function(item){
                                return item.property;
                            })
                            .filter(function(item){
                                return item.class === self.ontologyclass();
                            })
                            .pluck('property')
                            .value();
                    }
                }, this);
            }

            self.iconclass = ko.computed(function() {
                return self.datatypelookup[self.datatype()];
            });

            self.json = ko.computed(function() {
                return JSON.stringify(_.extend(JSON.parse(self._node()), {
                    name: self.name(),
                    datatype: self.datatype(),
                    nodegroup_id: self.nodeGroupId(),
                    validations: self.validations(),
                    ontologyclass: self.ontologyclass(),
                    parentproperty: self.parentproperty()
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
            self.ontologyclass(source.ontologyclass);
            self.parentproperty(source.parentproperty);
            self.validations.removeAll();
            source.validations.forEach(function(validation) {
                self.validations.push(validation);
            });

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

        getValidNodesEdges: function(){
            this.graph.getValidNodesEdges(this.nodeid, function(responseJSON){
                this.ontology_cache.removeAll();
                responseJSON.forEach(function(item){
                    item.ontology_classes.forEach(function(ontologyclass){
                        this.ontology_cache.push({
                            'property': item.ontology_property,
                            'class': ontologyclass
                        })
                    }, this);
                }, this);
            }, this);
        }
    });
});
