define([
    'underscore',
    'knockout',
    'arches',
    'models/abstract',
], function(_, ko, arches, AbstractModel) {
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
        initialize: function(options) {
            var self = this;
            self.graph = options.graph;
            self.datatypelookup = options.datatypelookup;
            self.layer = options.layer;
            self.icons = options.icons || [];
            self.mapSource = options.mapSource;
            self.loading = options.loading;
            self.permissions = options.permissions;
            self.ontology_namespaces = options.ontology_namespaces || {};
            if (options.url) {
                self.url = options.url;
            }

            if (options.source.config && _.keys(options.source.config).length === 0) {
                options.source.config = null;
            }

            self._node = ko.observable('');
            self.selected = ko.observable(false);
            self.filtered = ko.observable(false);
            self.name = ko.observable('');
            self.description = ko.observable(null);
            self.slug = ko.observable(null);
            self.alias = ko.observable(null);
            self.hasCustomAlias = ko.observable(false);
            self.nodeGroupId = ko.observable('');
            var datatype = ko.observable('');
            self.datatype = ko.computed({
                read: function() {
                    return datatype();
                },
                write: function(value) {
                    if (datatype() !== value) {
                        var datatypeRecord = self.datatypelookup[value];
                        if (datatypeRecord) {
                            var defaultConfig = datatypeRecord.defaultconfig;
                            self.setupConfig(defaultConfig);
                        }
                        datatype(value);
                    }
                },
                owner: this
            });

            self.datatypeDataBearing = ko.computed(function() {
                var result = false;
                if (self.datatype()) {
                    if (self.datatypelookup[self.datatype()]) {
                        result = !!self.datatypelookup[self.datatype()].defaultwidget_id;
                    }
                }
                return result;
            });

            self.datatypeIsSearchable = ko.computed(function() {
                var searchable = false;
                var datatype = self.datatypelookup[self.datatype()];
                if (datatype && datatype.configname) {
                    searchable = datatype.issearchable;
                }
                return searchable;
            });
            self.datatypeConfigComponent = ko.computed(function() {
                var component = null;
                var datatype = self.datatypelookup[self.datatype()];
                if (datatype && datatype.configname) {
                    component = datatype.configname;
                }
                return component;
            });
            self.ontologyclass = ko.observable('');
            self.parentproperty = ko.observable('');
            self.ontology_cache = ko.observableArray().extend({
                deferred: true
            });
            self.configKeys = ko.observableArray();
            self.config = {};
            self.issearchable = ko.observable(true);
            self.isrequired = ko.observable(true);
            self.fieldname = ko.observable();
            self.exportable = ko.observable(false);

            self.parse(options.source);

            self.validclasses = ko.computed(function() {
                if (!self.parentproperty()) {
                    return _.chain(self.ontology_cache())
                        .sortBy(function(item) {
                            return item.class;
                        })
                        .uniq(function(item) {
                            return item.class;
                        })
                        .pluck('class')
                        .value();
                } else {
                    return _.chain(self.ontology_cache())
                        .sortBy(function(item) {
                            return item.class;
                        })
                        .filter(function(item) {
                            return item.property === self.parentproperty();
                        })
                        .pluck('class')
                        .value();
                }
            }, this);

            if (!self.istopnode) {
                self.validproperties = ko.computed(function() {
                    if (!self.ontologyclass()) {
                        return _.chain(self.ontology_cache())
                            .sortBy(function(item) {
                                return item.property;
                            })
                            .uniq(function(item) {
                                return item.property;
                            })
                            .pluck('property')
                            .value();
                    } else {
                        return _.chain(self.ontology_cache())
                            .sortBy(function(item) {
                                return item.property;
                            })
                            .filter(function(item) {
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
                var jsObj = ko.toJS({
                    name: self.name,
                    datatype: self.datatype,
                    nodegroup_id: self.nodeGroupId,
                    description: self.description,
                    slug: self.slug,
                    ontologyclass: self.ontologyclass,
                    parentproperty: self.parentproperty,
                    config: config,
                    issearchable: self.issearchable,
                    isrequired: self.isrequired,
                    fieldname: self.fieldname,
                    exportable: self.exportable,
                    alias: self.alias,
                    hascustomalias: self.hasCustomAlias,
                    sourcebranchpublication_id: self.sourceBranchPublicationId
                });
                return JSON.stringify(_.extend(JSON.parse(self._node()), jsObj));
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._node();
            }).extend({ rateLimit: 100 });

            self.isCollector = ko.computed(function() {
                return self.nodeid === self.nodeGroupId();
            });

            self.selected.subscribe(function(selected) {
                if (selected) {
                    self.getValidNodesEdges();
                }
            });

            self.ontologyclass_friendlyname = ko.computed(function() {
                return self.getFriendlyOntolgyName(self.ontologyclass());
            });
            self.parentproperty_friendlyname = ko.computed(function() {
                return self.getFriendlyOntolgyName(self.parentproperty());
            });
        },

        /**
         * Gets the name for an ontology uri that is more user friendly
         * by using a namespace if possible
         * "http://www.cidoc-crm.org/cidoc-crm/E1_Entity" could become "E1_Entity"
         * @memberof NodeModel.prototype
         * @param {string} ontologyname - the ontology URI to get the friendly name for
         */
        getFriendlyOntolgyName: function(ontologyname){
            if(!!ontologyname){
                var uri = _.chain(this.ontology_namespaces)
                    .keys()
                    .find(function(namespace){
                        return ontologyname.indexOf(namespace) !== -1;
                    })
                    .value();

                if(!!uri){
                    var namespace = this.ontology_namespaces[uri];
                    if(!!namespace){
                        return ontologyname.replace(uri, namespace + ":");
                    }else{
                        return ontologyname.replace(uri, '');
                    }
                }else{
                    return ontologyname;
                }
            }else{
                return '';
            }
        },

        /**
         * Parses a js object and updates the model
         * @memberof NodeModel.prototype
         * @param {object} source - an object containing node data
         */
        parse: function(source) {
            var self = this;
            self._node(JSON.stringify(source));
            self.name(ko.unwrap(source.name));
            self.nodeGroupId(source.nodegroup_id);
            self.datatype(source.datatype);
            self.description(source.description);
            self.slug(source.slug);
            self.ontologyclass(source.ontologyclass);
            self.parentproperty(source.parentproperty);
            self.issearchable(source.issearchable);
            self.isrequired(source.isrequired);
            self.fieldname(source.fieldname);
            self.exportable(source.exportable);
            self.alias(source.alias);
            self.hasCustomAlias(source.hascustomalias);

            if (source.config) {
                self.setupConfig(source.config);
            }

            self.nodeid = source.nodeid;
            self.istopnode = source.istopnode;
            self.sourceBranchPublicationId = source.sourcebranchpublication_id;

            self.set('id', self.nodeid);
            self.set('graph_id', source.graph_id);
        },

        setupConfig: function(config) {
            var self = this;
            var keys = [];
            var datatypeRecord = this.datatypelookup[this.datatype()];
            if (datatypeRecord && datatypeRecord.defaultconfig && config) {
                var defaultConfig = datatypeRecord.defaultconfig;
                _.each(defaultConfig, function(value, key) {
                    if (!Object.prototype.hasOwnProperty.call(config, key)) {
                        config[key] = value;
                    }
                });
            }
            _.each(config, function(configVal, configKey) {
                if (!ko.isObservable(self.config[configKey])) {
                    self.config[configKey] = Array.isArray(configVal) ?
                        ko.observableArray(configVal) :
                        ko.observable(configVal);
                } else {
                    self.config[configKey](configVal);
                }
                keys.push(configKey);
            });
            self.configKeys(keys);
        },

        /**
         * discards unsaved model changes and resets the model data
         * @memberof NodeModel.prototype
         */
        reset: function() {
            this.parse(JSON.parse(this._node()), self);
        },

        save: function(userCallback, scope) {
            var method = "POST";
            var callback = function(request, status, model) {
                if (typeof userCallback === 'function') {
                    userCallback.call(this, request, status, model);
                }
                if (status==='success') {
                    this.alias(request.responseJSON.updated_values?.node.alias);
                    this._node(this.json());
                }
            };
            return this._doRequest({
                type: method,
                url: this._getURL(method),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'save');
        },

        /**
         * returns a JSON object containing model data
         * @memberof NodeModel.prototype
         * @return {object} a JSON object containing model data
         */
        toJSON: function() {
            return JSON.parse(this.json());
        },


        /**
         * toggles the isCollector state of the node model by managing group ids
         * @memberof NodeModel.prototype
         */
        toggleIsCollector: function() {
            var nodeGroupId = this.nodeid;
            var self = this;
            if (this.isCollector()) {
                nodeGroupId = this.graph.getParentNode(this).nodeGroupId();
            }
            var children  = this.graph.getChildNodesAndEdges(this).nodes;
            children.forEach(function(child) {
                if (child.nodeGroupId() === self.nodeGroupId()) {
                    child.nodeGroupId(nodeGroupId);
                    child._node(child.json());
                }
            });
            this.nodeGroupId(nodeGroupId);
        },

        /**
         * updates the cache of available ontology classes based on graph state
         * @memberof NodeModel.prototype
         */
        getValidNodesEdges: function() {
            this.graph.getValidNodesEdges(this.nodeid, function(responseJSON) {
                this.ontology_cache.removeAll();
                if (responseJSON !== undefined) {
                    responseJSON.forEach(function(item) {
                        item.ontology_classes.forEach(function(ontologyclass) {
                            this.ontology_cache.push({
                                'property': item.ontology_property,
                                'class': ontologyclass
                            });
                        }, this);
                    }, this);
                }
            }, this);
        },

        _getURL: function(method){
            var id = this.get('graph_id');
            if(!(id)){
                id = '';
            }
            if(this.url.indexOf('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa') > -1){
                return this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', id);
            }else{
                return this.url + id;
            }
        },
    });
});
