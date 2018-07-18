define(['arches',
    'models/abstract',
    'models/node',
    'models/card-widget',
    'knockout',
    'knockout-mapping'
], function(arches, AbstractModel, NodeModel, CardWidgetModel, ko, koMapping) {
    var deepDiffMapper = function() {
    return {
        VALUE_CREATED: 'created',
        VALUE_UPDATED: 'updated',
        VALUE_DELETED: 'deleted',
        VALUE_UNCHANGED: 'unchanged',
        map: function(obj1, obj2) {
            if (this.isFunction(obj1) || this.isFunction(obj2)) {
                //throw 'Invalid argument. Function given, object expected.';
            }
            if (this.isValue(obj1) || this.isValue(obj2)) {
                return {
                    type: this.compareValues(obj1, obj2),
                    data: (obj1 === undefined) ? obj2 : obj1
                };
            }

            var diff = {};
            for (var key in obj1) {
                if (this.isFunction(obj1[key])) {
                    continue;
                }

                var value2 = undefined;
                if ('undefined' != typeof(obj2[key])) {
                    value2 = obj2[key];
                }

                diff[key] = this.map(obj1[key], value2);
            }
            for (var key in obj2) {
                if (this.isFunction(obj2[key]) || ('undefined' != typeof(diff[key]))) {
                    continue;
                }

                diff[key] = this.map(undefined, obj2[key]);
            }

            return diff;

        },
        compareValues: function(value1, value2) {
            if (value1 === value2) {
                return this.VALUE_UNCHANGED;
            }
            if (this.isDate(value1) && this.isDate(value2) && value1.getTime() === value2.getTime()) {
                return this.VALUE_UNCHANGED;
            }
            if ('undefined' == typeof(value1)) {
                return this.VALUE_CREATED;
            }
            if ('undefined' == typeof(value2)) {
                return this.VALUE_DELETED;
            }

            return this.VALUE_UPDATED;
        },
        isFunction: function(obj) {
            return {}.toString.apply(obj) === '[object Function]';
        },
        isArray: function(obj) {
            return {}.toString.apply(obj) === '[object Array]';
        },
        isDate: function(obj) {
            return {}.toString.apply(obj) === '[object Date]';
        },
        isObject: function(obj) {
            return {}.toString.apply(obj) === '[object Object]';
        },
        isValue: function(obj) {
            return !this.isObject(obj) && !this.isArray(obj);
        }
        }
    }();
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
            this.helptext = ko.observable();
            this.helpenabled = ko.observable();
            this.helptitle = ko.observable();
            this.helpactive = ko.observable(false);
            this.cardinality = ko.observable();
            this.visible = ko.observable();
            this.active = ko.observable();
            this.ontologyproperty = ko.observable();
            this.sortorder = ko.observable();
            this.disabled = ko.observable();
            this.component_id = ko.observable();

            this.set('cards', this.cards);
            this.set('nodes', this.nodes);
            this.set('widgets', this.widgets);
            this.set('tiles', this.tiles);

            this.set('cardid', this.cardid);
            this.set('nodegroup_id', this.nodegroup_id);
            this.set('name', this.name);
            this.set('instructions', this.instructions);
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

            this._card = ko.observable('{}');

            this.get('cards').subscribe(function(cards) {
                _.each(cards, function(card, i) {
                    card.get('sortorder')(i);
                });
            });

            this.get('widgets').subscribe(function(widgets) {
                _.each(widgets, function(widget, i) {
                    widget.get('sortorder')(i);
                });
            });

            this.dirty = ko.computed(function() {
                // console.log('current')
                // console.log(_.extend(JSON.parse(self._card()), self.toJSON()))
                // console.log('old')
                // console.log(JSON.parse(self._card()))
                //console.log(deepDiffMapper.map(_.extend(JSON.parse(self._card()), self.toJSON()), JSON.parse(self._card())));
                console.log(deepDiffMapper.map(JSON.parse(self._card()), _.extend(JSON.parse(self._card()), self.toJSON())));
                return JSON.stringify(_.extend(JSON.parse(self._card()), self.toJSON())) !== self._card();
            });

            this.isContainer = ko.computed(function() {
                return !!self.get('cards')().length;
            });

            this.parse(attributes);
            this.parseNodes.call(this, attributes);

            attributes.data.nodes.subscribe(function(){
                this.parseNodes(attributes);
                this._card(JSON.stringify(this.toJSON()));
            }, this);
        },

        /**
         * parse - parses the passed in attributes into a {@link CardModel}
         * @memberof CardModel.prototype
         * @param  {object} attributes - the properties to seed a {@link CardModel} with
         */
        parse: function(attributes) {
            var self = this;
            var datatypelookup = {};

            attributes = _.extend({datatypes: []}, attributes);
            this._attributes = attributes;

            _.each(attributes.datatypes, function(datatype) {
                datatypelookup[datatype.datatype] = datatype;
            }, this);
            this.set('datatypelookup', datatypelookup);

            _.each(attributes.data, function(value, key) {
                switch (key) {
                case 'cards':
                    var cards = [];
                    var cardData = _.sortBy(value, 'sortorder');
                    cardData.forEach(function(card) {
                        var cardModel = new CardModel({
                            data: card,
                            datatypes: attributes.datatypes
                        });
                        cards.push(cardModel);
                    }, this);
                    this.get('cards')(cards);
                    break;
                // case 'nodes':
                //     this.parseNodes(attributes);
                //     break;
                case 'widgets':
                    break;
                case 'cardid':
                    this.set('id', value);
                    this.get(key)(value);
                    break;
                case 'name':
                case 'nodegroup_id':
                case 'instructions':
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

        parseNodes: function(attributes) {
            console.log('in parse nodes');
            var widgets = [];
            var nodeArray = [];
            //this.get('widgets').removeAll();
            ko.unwrap(this.nodes).forEach(function(node, i) {
                if(ko.unwrap(node.nodeGroupId) === ko.unwrap(attributes.data.nodegroup_id)){
                    var datatype = _.find(attributes.datatypes, function(datatype) {
                        return datatype.datatype === ko.unwrap(node.datatype);
                    });
                    node.datatype.subscribe(function(){
                        this.parseNodes(attributes);
                        this._card(JSON.stringify(this.toJSON()));
                    }, this);
                    node.config = koMapping.fromJS(node.config);
                    
                    if (datatype.defaultwidget_id) {
                        var cardWidgetData = _.find(attributes.data.widgets, function(widget) {
                            return widget.node_id === node.nodeid;
                        });
                        var widget = new CardWidgetModel(cardWidgetData, {
                            node: node,
                            card: this,
                            datatype: datatype,
                            disabled: attributes.data.disabled,
                            widgetList: attributes.widgetList
                        });
                        //widgets.push(widget);
                        this.get('widgets').push(widget);
                    }
                    //nodeArray.push(node);
                }
            }, this);
            //this.get('nodes')(nodeArray);
            this.get('widgets').sort(function(w, ww) {
                return w.get('sortorder')() > ww.get('sortorder')();
            });
            //this.get('widgets')(widgets);
        },

        reset: function() {
            this._attributes.data = JSON.parse(this._card());
            this.get('widgets')().forEach(function(widget){
                var origData = _.find(this._attributes.data.widgets, function(origwidget){
                    return widget.widget_id() === origwidget.widget_id;
                });
                if (origData) {
                    console.log(widget.configKeys())
                    widget.configKeys().forEach(function(configKey){
                        widget.config[configKey](origData.config[configKey]);
                    })
                }
            }, this);
            this.parse(this._attributes);
        },

        toJSON: function() {
            var ret = {};
            for (var key in this.attributes) {
                if (key !== 'datatypelookup' && key !== 'ontology_properties' && key !== 'nodes' &&
                 key !== 'widgets' && key !== 'datatypes' && key !== 'data' && key !== 'widgetList') {
                    if (ko.isObservable(this.attributes[key])) {
                        if (key === 'cards') {
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
                    // ret['nodes'] = _.map(widgets, function(widget) {
                    //     return widget.node.toJSON();
                    // });
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
