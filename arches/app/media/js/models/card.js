define([
    'underscore',
    'arches',
    'models/abstract',
    'models/node',
    'models/card-widget',
    'knockout',
    'knockout-mapping',
    'card-components',
    'viewmodels/card-constraints',
    'utils/dispose'
], function(_, arches, AbstractModel, NodeModel, CardWidgetModel, ko, koMapping, cardComponentLookup, CardConstraintsViewModel, dispose) {
    var CardModel = AbstractModel.extend({
        /**
        * A backbone model to manage card data
        * @augments AbstractModel
        * @constructor
        * @name CardModel
        */

        url: arches.urls.card,

        initialize: function(attributes) {
            var self = this;
            this.cards = ko.observableArray();
            this.nodes = attributes.data.nodes;
            this.widgets = ko.observableArray();
            this.tiles = ko.observableArray();

            this.cardid = ko.observable();
            this.nodegroup_id = ko.observable();
            this.name = ko.observable();
            this.instructions = ko.observable();
            this.cssclass = ko.observable();
            this.helptext = ko.observable();
            this.helpenabled = ko.observable();
            this.helptitle = ko.observable();
            this.helpactive = ko.observable(false);
            this.cardinality = ko.observable();
            if (attributes.data.nodegroup) {
                this.cardinality(attributes.data.nodegroup.cardinality);
            }
            this.visible = ko.observable();
            this.active = ko.observable();
            this.ontologyproperty = ko.observable();
            this.sortorder = ko.observable();
            this.disabled = ko.observable();
            this.component_id = ko.observable();
            this.constraints = ko.observableArray();
            this.appliedFunctions = attributes.appliedFunctions;

            this.set('cards', this.cards);
            this.set('nodes', this.nodes);
            this.set('widgets', this.widgets);
            this.set('tiles', this.tiles);

            this.set('cardid', this.cardid);
            this.set('nodegroup_id', this.nodegroup_id);
            this.set('cardinality', this.cardinality);
            this.set('name', this.name);
            this.set('instructions', this.instructions);
            this.set('cssclass', this.cssclass);
            this.set('helptext', this.helptext);
            this.set('helpenabled', this.helpenabled);
            this.set('helptitle', this.helptitle);
            this.set('helpactive', this.helpactive);
            this.set('cardinality', this.cardinality);
            this.set('visible', this.visible);
            this.set('active', this.active);
            this.set('ontologyproperty', this.ontologyproperty);
            this.set('sortorder', this.sortorder);
            this.set('disabled', this.disabled);
            this.set('component_id', this.component_id);
            this.set('config', {});
            this.set('constraints', this.constraints);
            this.set('appliedFunctions', this.appliedFunctions);

            this.cardComponentLookup = cardComponentLookup;
            this.configKeys = ko.observableArray();
            this.disposables = [];

            this.configJSON = ko.computed({
                read: function() {
                    var configJSON = {};
                    var config = this.get('config');
                    _.each(this.configKeys(), function(key) {
                        configJSON[key] = ko.unwrap(config[key]);
                    });
                    return configJSON;
                },
                write: function(value) {
                    var config = this.get('config');
                    for (var key in value) {
                        if (config[key] && config[key]() !== value[key]) {
                            config[key](value[key]);
                        }
                    }
                },
                owner: this
            });

            var componentIdSubscription = this.get('component_id').subscribe(function(value) {
                var key;
                var defaultConfig = JSON.parse(self.cardComponentLookup[value].defaultconfig);
                for (key in defaultConfig) {
                    defaultConfig[key] = ko.observable(defaultConfig[key]);
                }
                var currentConfig = self.get('config');
                self.set('config', _.defaults(currentConfig, defaultConfig));
                for (key in defaultConfig) {
                    self.configKeys.push(key);
                }
            });

            this._card = ko.observable('{}');

            this.dirty = ko.computed(function() {
                return JSON.stringify(
                    _.extend(
                        JSON.parse(self._card()),
                        self.toJSON())
                ) !== self._card();
            });

            this.isContainer = ko.computed(function() {
                return !!self.get('cards')().length;
            });

            this.setConstraints = function(arr) {
                var self = this;
                if (arr) {
                    arr.forEach(function(constraint){
                        var constraintViewModel = new CardConstraintsViewModel({
                            constraint: koMapping.fromJS(constraint),
                            widgets: self.widgets()
                        });
                        constraintViewModel.constraint.nodes.subscribe(function(){
                            self.toJSON();
                        }, self);
                        self.constraints.push(constraintViewModel);
                    });
                }
            };

            this.sourceData = attributes;
            this.parse(attributes);
            this.parseNodes.call(this, attributes);

            var cardSubscription = this.get('cards').subscribe(function(cards) {
                _.each(cards, function(card, i) {
                    card.get('sortorder')(i);
                });
            });

            var widgetSubscription = this.get('widgets').subscribe(function(widgets) {
                _.each(widgets, function(widget, i) {
                    widget.get('sortorder')(i);
                });
            });

            var nodes = ko.computed(function() {
                return attributes.data.nodes();
            }, this).extend({ throttle: 100 });

            var nodesSubscription = nodes.subscribe(function(){
                this.parseNodes(attributes);
            }, this);

            this.disposables.push(componentIdSubscription);
            this.disposables.push(cardSubscription);
            this.disposables.push(widgetSubscription);
            this.disposables.push(nodes);
            this.disposables.push(nodesSubscription);
            this.disposables.push(this.configJSON);
            this.disposables.push(this.dirty);
            this.disposables.push(this.isContainer);

            this.dispose = function() {
                //console.log('disposing CardModel');
                dispose(self);
            };
        },

        /**
         * parse - parses the passed in attributes into a {@link CardModel}
         * @memberof CardModel.prototype
         * @param  {object} attributes - the properties to seed a {@link CardModel} with
         */
        parse: function(attributes) {
            var self = this;
            // console.log(attributes.data.constraints[0].nodes)
            // console.log(attributes.data.constraints[0].nodes)
            this._attributes = attributes;

            _.each(attributes.data, function(value, key) {
                switch (key) {
                case 'config':
                    var config = {};
                    var configKeys = [];
                    self.configKeys.removeAll();
                    _.each(value, function(configVal, configKey) {
                        if (!ko.isObservable(configVal)) {
                            configVal = koMapping.fromJS(configVal);
                        }
                        config[configKey] = configVal;
                        configKeys.push(configKey);
                    });
                    this.set(key, config);
                    self.configKeys(configKeys);
                    break;
                case 'cards':
                    var cards = [];
                    var cardData = _.sortBy(value, 'sortorder');
                    cardData.forEach(function(card) {
                        var cardModel = new CardModel({
                            data: _.extend(card, {
                                nodes: attributes.data.nodes
                            }),
                            datatypelookup: attributes.datatypelookup,
                            cardComponents: attributes.cardComponents
                        });
                        cards.push(cardModel);
                    }, this);
                    this.get('cards')(cards);
                    break;
                case 'widgets':
                    break;
                case 'cardid':
                    this.set('id', value);
                    this.get(key)(value);
                    break;
                case 'constraints':
                    if (this.constraints().length === 0) {
                        this.setConstraints(value);
                    } else {
                        this.constraints().forEach(function(constraint, i){
                            constraint.update(value[i]);
                        });
                    }
                    break;
                case 'name':
                case 'nodegroup_id':
                case 'instructions':
                case 'cssclass':
                case 'helptext':
                case 'helpenabled':
                case 'helptitle':
                case 'cardinality':
                case 'visible':
                case 'active':
                case 'ontologyproperty':
                case 'sortorder':
                case 'component_id':
                    this.get(key)(value);
                    break;
                case 'ontology_properties':
                case 'tiles':
                    this.set(key, koMapping.fromJS(value));
                    break;
                default:
                    this.set(key, value);
                }
            }, this);
            this._card(JSON.stringify(this.toJSON()));
        },

        parseNodes: function() {
            var self = this;
            var attributes = this.sourceData;
            var nodeIds = [];

            var widgetNodeIds = ko.unwrap(this.get('widgets')).map(function(widget) {
                return ko.unwrap(widget.node_id);
            });

            // let's iterate over each node, and add any new widgets
            ko.unwrap(this.nodes).forEach(function(node) {
                nodeIds.push(node.id);

                // TODO: it would be nice to normalize the nodegroup_id names (right now we have several different versions)
                var nodegroupId = ko.unwrap(node.nodeGroupId) || ko.unwrap(node.nodegroup_id);

                if (nodegroupId === ko.unwrap(attributes.data.nodegroup_id) && !widgetNodeIds.includes(node.nodeid)) {
                    var datatype = attributes.datatypelookup[ko.unwrap(node.datatype)];

                    var nodeDatatypeSubscription = node.datatype.subscribe(function(){
                        this._card(JSON.stringify(this.toJSON()));
                    }, this);
                    this.disposables.push(nodeDatatypeSubscription);
    
                    if (datatype.defaultwidget_id) {
                        var cardWidgetData = _.find(attributes.data.widgets, function(widget) {
                            return widget.node_id === node.nodeid;
                        });
                        var widget = new CardWidgetModel(cardWidgetData, {
                            node: node,
                            card: this,
                            datatype: datatype,
                            disabled: attributes.data.disabled
                        });
                        this.get('widgets').push(widget);
                    }
                }
            }, this);

            // let's iterate over each widget, and remove any orphans
            var widgetsToDelete = ko.unwrap(this.get('widgets')).filter(function(widget) {
                var widgetNodegroupId = ko.unwrap(widget.node.nodeGroupId) || ko.unwrap(widget.node.nodegroup_id);

                if (ko.unwrap(this.nodegroup_id) !== widgetNodegroupId || !nodeIds.includes(widget.node_id())) {
                    return widget;
                }
            }, this);

            widgetsToDelete.forEach(function(widget) {
                this.get('widgets').remove(widget);  
            }, this);
            
            // let's sort the widgets according to sortorder
            this.get('widgets').sort(function(w, ww) {
                return w.get('sortorder')() - ww.get('sortorder')();
            });

            this._card(JSON.stringify(this.toJSON()));
        },

        reset: function() {
            this._attributes.data = JSON.parse(this._card());
            this.get('widgets')().forEach(function(widget){
                var originalWidgetData = _.find(this._attributes.data.widgets, function(origwidget){
                    return widget.node_id() === origwidget.node_id;
                });
                if (originalWidgetData) {
                    widget.configKeys().forEach(function(configKey){
                        koMapping.fromJS(originalWidgetData.config[configKey], widget.config[configKey]);
                    });
                    widget.label(originalWidgetData.label);
                    widget.widget_id(originalWidgetData.widget_id);
                }
            }, this);
            this.parse(this._attributes);
        },

        toJSON: function() {
            var self = this;
            var ret = {};
            for (var key in this.attributes) {
                if (key !== 'datatypelookup' && key !== 'ontology_properties' && key !== 'nodes' &&
                 key !== 'widgets' && key !== 'datatypes' && key !== 'data' && key !== 'helpactive' &&
                 key !== 'config') {
                    if (ko.isObservable(this.attributes[key])) {
                        if (key === 'constraints') {
                            ret[key] = [];
                            this.attributes[key]().forEach(function(constraint) {
                                ret[key].push(constraint.toJSON());
                            }, this);
                        } else if (key === 'cards') {
                            ret[key] = [];
                            this.attributes[key]().forEach(function(card) {
                                ret[key].push(card.toJSON());
                            }, this);
                        } else {
                            ret[key] = this.attributes[key]();
                        }
                    } else {
                        ret[key] = this.attributes[key];
                    }
                } else if (key === 'widgets') {
                    var widgets = this.attributes[key]();
                    ret[key] = _.map(widgets, function(widget) {
                        return widget.toJSON();
                    });
                } else if (key === 'config') {
                    var configKeys = this.configKeys();
                    var config = null;
                    if (configKeys.length > 0) {
                        config = {};
                        _.each(configKeys, function(configKey) {
                            config[configKey] = ko.unwrap(self.get('config')[configKey]);
                        });
                    }
                    ret[key] = config;
                }
            }
            return ret;
        },

        save: function(callback) {
            AbstractModel.prototype.save.call(this, function(request, status, self) {
                if (status === 'success') {
                    this._card(JSON.stringify(this.toJSON()));
                }
                if (typeof callback === 'function') {
                    callback(request, status, self);
                }
            }, this);
        }

    });
    return CardModel;
});
