define(['underscore', 'knockout', 'models/abstract'], function (_, ko, AbstractModel) {
    return AbstractModel.extend({
        defaults: {
            'id': null,
            'node_id': '',
            'card_id': '',
            'widget_id': '',
            'inputmask': '',
            'inputlabel': ''
        },

        constructor: function(attributes, options){
            options || (options = {});
            options.parse = true;
            this.node = (options.node || null);
            this.card = (options.card || null);
            this.datatypes = (options.datatypes || []);
            AbstractModel.prototype.constructor.call(this, attributes, options);
        },

        parse: function(attributes){
            var self = this;
            attributes || (attributes = {});

            attributes = _.defaults(attributes, this.defaults);

            _.each(attributes, function(value, key){
                this.set(key, ko.observable(value));
            }, this);
        }
    });
});
