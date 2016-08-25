define([
    'knockout',
    'models/abstract',
    'arches'
], function (ko, AbstractModel, arches) {
    return AbstractModel.extend({
        /**
        * A backbone model representing a single node in a graph
        * @augments AbstractModel
        * @constructor
        * @name NodeModel
        */
        url: arches.urls.node,

        /**
        * Initializes the model with optional parameters
        * @memberof NodeModel.prototype
        * @param {object} options
        * @param {object} options.graph - a reference to the parent {@link GraphModel}
        * @param {array} options.datatypelookup - an array of datatype objects
        * @param {object} options.source - an object containing node data
        */
        initialize: function (options) {
            var self = this;
            self.graph = options.graph;
            self.datatypelookup = options.datatypelookup;

            self._node = ko.observable('');
            self.selected = ko.observable(false);
            self.filtered = ko.observable(false);
            self.name = ko.observable('');
            self.nodeGroupId = ko.observable('');
            var datatype = ko.observable('');
            self.datatype = ko.computed({
                read: function () {
                    return datatype();
                },
                write: function (value) {
                    var datatypeRecord = self.datatypelookup[value];
                    if (datatypeRecord) {
                        var defaultConfig = datatypeRecord.defaultconfig;
                        self.configKeys.removeAll();
                        _.each(defaultConfig, function(configVal, configKey) {
                            self.config[configKey] = ko.observable(configVal);
                            self.configKeys.push(configKey);
                        });
                    }
                    datatype(value);
                },
                owner: this
            });
            self.validations = ko.observableArray();
            self.ontologyclass = ko.observable('');
            self.parentproperty = ko.observable('');
            self.ontology_cache = ko.observableArray().extend({ deferred: true });
            self.configKeys = ko.observableArray();
            self.config = {};


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
                var datatypeRecord = self.datatypelookup[self.datatype()];
                if (!datatypeRecord) {
                    return '';
                }
                return datatypeRecord.iconclass;
            });

            self.json = ko.computed(function() {
                var keys = self.configKeys();
                var config = null;
                if (keys.length > 0) {
                    config = {};
                    _.each(keys, function(key) {
                        config[key] = self.config[key]();
                    });
                }
                return JSON.stringify(_.extend(JSON.parse(self._node()), {
                    name: self.name(),
                    datatype: self.datatype(),
                    nodegroup_id: self.nodeGroupId(),
                    validations: self.validations(),
                    ontologyclass: self.ontologyclass(),
                    parentproperty: self.parentproperty(),
                    config: config
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

        /**
        * Parses a js object and updates the model
        * @memberof NodeModel.prototype
        * @param {object} source - an object containing node data
        */
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

            if (source.config) {
                self.configKeys.removeAll();
                _.each(source.config, function(configVal, configKey) {
                    self.config[configKey] = ko.observable(configVal);
                    self.configKeys.push(configKey);
                });
            }

            self.nodeid = source.nodeid;
            self.istopnode = source.istopnode;

            self.set('id', self.nodeid);
        },

        /**
        * discards unsaved model changes and resets the model data
        * @memberof NodeModel.prototype
        */
        reset: function () {
            this.parse(JSON.parse(this._node()), self);
        },

        /**
        * returns a JSON object containing model data
        * @memberof NodeModel.prototype
        * @return {object} a JSON object containing model data
        */
        toJSON: function () {
            return JSON.parse(this.json());
        },


        /**
        * toggles the isCollector state of the node model by managing group ids
        * @memberof NodeModel.prototype
        */
        toggleIsCollector: function () {
            var nodeGroupId = this.nodeid;
            if (this.isCollector()) {
                var _node = JSON.parse(this._node());
                nodeGroupId = (this.nodeid === _node.nodegroup_id) ? null : _node.nodegroup_id;
            }
            this.nodeGroupId(nodeGroupId);
        },

        /**
        * updates the cache of available ontology classes based on graph state
        * @memberof NodeModel.prototype
        */
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
