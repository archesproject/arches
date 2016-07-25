define(['underscore', 'knockout', 'models/abstract'], function (_, ko, AbstractModel) {
    return AbstractModel.extend({
        constructor: function(attributes, options){
            var defaults = {
                'id': null,
                'node_id': '',
                'card_id': '',
                'widget_id': '',
                'config': {},
                'label': ''
            };
            options || (options = {});
            attributes || (attributes = {});
            options.parse = true;
            this.node = (options.node || null);
            this.card = (options.card || null);
            this.datatype = (options.datatype || null);
            if (this.datatype && this.datatype.defaultwidget_id) {
                defaults.widget_id = this.datatype.defaultwidget_id;
            }
            if (this.node) {
                defaults.label = this.node.name();
            }

            attributes = _.defaults(attributes, defaults);
            return AbstractModel.prototype.constructor.call(this, attributes, options);
        },

        parse: function(attributes){
            var self = this;

            _.each(attributes, function(value, key){
                this.set(key, ko.observable(value));
            }, this);
        }
    });
});
