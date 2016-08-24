define(['arches',
    'models/abstract',
    'models/node',
    'models/card-widget',
    'knockout',
    'knockout-mapping',
    'underscore'
], function (arches, AbstractModel, NodeModel, CardWidgetModel, ko, koMapping, _) {
    var CardModel = AbstractModel.extend({
        /**
        * A backbone model to manage card data
        * @augments AbstractModel
        * @constructor
        * @name CardModel
        */

        url: arches.urls.card,

        constructor: function(attributes, options){
            options || (options = {});
            options.parse = true;
            AbstractModel.prototype.constructor.call(this, attributes, options);
        },

        /**
         * parse - parses the passed in attributes into a {@link CardModel}
         * @memberof CardModel.prototype
         * @param  {object} attributes - the properties to seed a {@link CardModel} with
         */
        parse: function(attributes){
            var self = this;
            var datatypelookup = {};

            attributes =_.extend({datatypes:[]}, attributes);

            _.each(attributes.datatypes, function(datatype){
                datatypelookup[datatype.datatype] = datatype.iconclass;
            }, this)
            this.set('datatypelookup', datatypelookup);

            var widgets = [];
            _.each(attributes.data, function(value, key){
                switch(key) {
                    case 'cards':
                        var cards = [];
                        var cardData = _.sortBy(value, 'sortorder');
                        cardData.forEach(function (card) {
                            var cardModel = new CardModel({
                                data: card,
                                datatypes: attributes.datatypes
                            });
                            cards.push(cardModel);
                        }, this);
                        this.set('cards', ko.observableArray(cards));
                        this.get('cards').subscribe(function (cards) {
                            _.each(cards, function(card, i) {
                                card.get('sortorder')(i);
                            })
                        });
                        break;
                    case 'nodes':
                        var nodes = [];
                        value.forEach(function (node, i) {
                            var nodeModel = new NodeModel({
                                source: node,
                                datatypelookup: datatypelookup,
                                graph: undefined
                            });
                            var datatype = _.find(attributes.datatypes, function(datatype) {
                                return datatype.datatype === node.datatype;
                            });
                            if (datatype.defaultwidget_id) {
                                var cardWidgetData = _.find(attributes.data.widgets, function(widget) {
                                    return widget.node_id === nodeModel.nodeid;
                                });
                                nodeModel.widget = new CardWidgetModel(cardWidgetData, {
                                    node: nodeModel,
                                    card: self,
                                    datatype: datatype
                                });
                                widgets.push(nodeModel.widget);
                            }
                            nodes.push(nodeModel);
                        }, this);
                        this.set('nodes', ko.observableArray(nodes));
                        break;
                    case 'widgets':
                        break;
                    case 'cardid':
                        this.set('id', value);
                    case 'name':
                    case 'instructions':
                    case 'helptext':
                    case 'helpenabled':
                    case 'helptitle':
                    case 'cardinality':
                    case 'visible':
                    case 'active':
                    case 'itemtext':
                    case 'ontologyproperty':
                    case 'sortorder':
                        this.set(key, ko.observable(value));
                        break;
                    case 'ontology_properties':
                    case 'users':
                    case 'groups':
                        this.set(key, koMapping.fromJS(value));
                        break;
                    case 'functions':
                        this.set(key, ko.observableArray(value));
                        break;
                    default:
                        this.set(key, value);
                }
            }, this);
            widgets = ko.observableArray(widgets).sort(function (w, ww) {
                return w.get('sortorder')() > ww.get('sortorder')();
            });
            this.set('widgets', widgets);
            this.get('widgets').subscribe(function (widgets) {
                _.each(widgets, function(widget, i) {
                    widget.get('sortorder')(i);
                });
            });

            this._card = ko.observable(JSON.stringify(this.toJSON()));

            this.dirty = ko.computed(function(){
                return JSON.stringify(_.extend(JSON.parse(self._card()),self.toJSON())) !== self._card();
            })

            this.isContainer = ko.computed(function() {
                return !!self.get('cards')().length;
            });
        },

        toJSON: function(){
            var ret = {};
            for(var key in this.attributes){
                if(key !== 'datatypelookup' && key !== 'ontology_properties' && key !== 'nodes' && key !== 'widgets'){
                    if(ko.isObservable(this.attributes[key])){
                        if(key === 'users' || key === 'groups'){
                            ret[key] = koMapping.toJS(this.attributes[key]);
                        }else if(key === 'cards'){
                            ret[key] = [];
                            this.attributes[key]().forEach(function(card){
                                ret[key].push(card.toJSON());
                            }, this)
                        }else{
                            ret[key] = this.attributes[key]();
                        }
                    }else{
                        ret[key] = this.attributes[key];
                    }
                } else if (key === 'widgets') {
                    var widgets = this.attributes[key]();
                    ret[key] = _.map(widgets, function (widget) {
                        return widget.toJSON();
                    });
                    ret['nodes'] = _.map(widgets, function (widget) {
                        return widget.node.toJSON();
                    });
                }
            }
            return ret;
        },

        save: function(){
            AbstractModel.prototype.save.call(this, function(request, status, self){
                if(status === 'success'){
                    // only user permissions data needs to be updated from the response because it's value can
                    // vary based on the groups (and their permissions) to which the users belong
                    var users = this.get('users')();
                    users.forEach(function(user){
                        var updatedUser = _.find(request.responseJSON.users, function(item){
                            return item.id === user.id();
                        })
                        user.perms.local.removeAll();
                        updatedUser.perms.local.forEach(function(perm){
                            user.perms.local.push(perm);
                        });
                        user.perms.default.removeAll();
                        updatedUser.perms.default.forEach(function(perm){
                            user.perms.default.push(perm);
                        });
                    })
                    this._card(JSON.stringify(this.toJSON()));
                }
            }, this);
        }
    });
    return CardModel;
});
