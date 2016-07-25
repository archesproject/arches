define(['underscore', 'knockout', 'models/abstract', 'widgets'], function (_, ko, AbstractModel, widgets) {
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
                defaults.config = widgets[defaults.widget_id].defaultconfig;
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
                if (key === 'config' && typeof value === 'string') {
                    value = JSON.parse(value);
                    var configKeys = [];
                    _.each(value, function(configVal, configKey) {
                        value[configKey] = ko.observable(configVal);
                        configKeys.push(configKey);
                    });
                    this.set(key, value);
                    this.configKeys = configKeys;
                } else {
                    this.set(key, ko.observable(value));
                }
            }, this);

            this.configJSON = ko.computed(function () {
                var configJSON = {};
                var config = self.get('config');
                _.each(self.configKeys, function(key) {
                    configJSON[key] = config[key]();
                });
                return configJSON;
            });
        }
    });
});
