define(['arches',
    'models/abstract',
    'models/node',
    'models/card-widget',
    'knockout',
    'knockout-mapping',
    'underscore'
], function(arches, AbstractModel, NodeModel, CardWidgetModel, ko, koMapping, _) {
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

            this.dirty = ko.computed(function() {
                return JSON.stringify(_.extend(JSON.parse(self._card()), self.toJSON())) !== self._card();
            });

            this.parse(attributes);
        },

        /**
         * parse - parses the passed in attributes into a {@link CardModel}
         * @memberof CardModel.prototype
         * @param  {object} attributes - the properties to seed a {@link CardModel} with
         */
        parse: function(attributes) {
            var self = this;

            this._attributes = attributes;

            _.each(attributes.data, function(value, key) {
                switch (key) {
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
                default:
                    this.set(key, value);
                }
            }, this);

            this._card(JSON.stringify(this.toJSON()));
        },

        reset: function() {
            this._attributes.data = JSON.parse(this._card());
            this.parse(this._attributes);
        },

        toJSON: function() {
            var ret = {};
            for (var key in this.attributes) {
                if (key !== 'data') {
                    ret[key] = ko.unwrap(this.attributes[key]);
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
