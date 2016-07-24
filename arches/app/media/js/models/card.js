define(['arches',
    'models/abstract',
    'models/node',
    'models/card-widget',
    'knockout',
    'underscore'
], function (arches, AbstractModel, NodeModel, CardWidgetModel, ko, _) {
    var CardModel = AbstractModel.extend({
        /**
        * A backbone model to manage graph data
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
                        value.forEach(function (card) {
                            var cardModel = new CardModel({
                                data: card,
                                datatypes: attributes.datatypes
                            });
                            cards.push(cardModel);
                        }, this);
                        this.set('cards', ko.observableArray(cards));
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
                    case 'cardinality':
                    case 'visible':
                    case 'active':
                    case 'ontologyproperty':
                        this.set(key, ko.observable(value));
                        break;
                    case 'ontology_properties':
                        this.set(key, ko.observableArray(value));
                        break;
                    default:
                        this.set(key, value);
                }
            }, this);

            this.set('widgets', ko.observableArray(widgets));

            this.isContainer = ko.computed(function() {
                return !!self.get('cards')().length;
            });
        },

        toJSON: function(){
            var ret = {};
            for(key in this.attributes){
                if(key !== 'datatypelookup'){
                    if(ko.isObservable(this.attributes[key])){
                        ret[key] = this.attributes[key]();
                    }else{
                        ret[key] = this.attributes[key];
                    }
                }
            }
            return ret;
        }
    });
    return CardModel;
});
