define([
    'underscore',
    'knockout',
    'arches',
    'knockout-mapping',
    'models/abstract',
    'widgets',
    'utils/dispose'
], function(_, ko, arches, koMapping, AbstractModel, widgets, dispose) {
    return AbstractModel.extend({
        /**
        * A backbone model to manage cards_x_nodes_x_widgets records
        * @augments AbstractModel
        * @constructor
        * @name CardWidgetModel
        */
        constructor: function(attributes, options){
            var defaults = {
                'id': null,
                'node_id': '',
                'card_id': '',
                'widget_id': '',
                'config': {},
                'label': '',
                'visible': true,
                'sortorder': null,
                'disabled': false
            };
            var self = this;
            this.disposables = [];
            this.widgetLookup = widgets;
            this.widgetList = function() {
                var widgets = _.map(self.widgetLookup, function(widget, id) {
                    widget.id = id;
                    return widget;
                });
                return _.filter(widgets, function(widget) {
                    return widget.datatype === self.datatype.datatype;
                });
            };
            options = options ? options : {};
            attributes = attributes ? attributes : {};
            options.parse = true;
            this.node = (options.node || null);
            this.card = (options.card || null);
            this.datatype = (options.datatype || null);
            this.disabled = (options.disabled || false);
            this.icon = 'ion-ios-paper';
            if (this.datatype) {
                this.icon = this.datatype.iconclass;
            }
            if (this.datatype && this.datatype.defaultwidget_id) {
                defaults.widget_id = this.datatype.defaultwidget_id;
                defaults.config = JSON.parse(widgets[defaults.widget_id].defaultconfig);
            }
            if (this.node) {
                defaults.node_id = this.node.nodeid;
                defaults.label = ko.unwrap(this.node.name);
            }
            if (this.card) {
                defaults.card_id = this.card.get('id');
            }

            attributes = _.defaults(attributes, defaults);

            AbstractModel.prototype.constructor.call(this, attributes, options);

            this.configJSON = ko.computed({
                read: function() {
                    var configJSON = {};
                    var config = this.get('config');
                    _.each(this.configKeys(), function(key) {
                        configJSON[key] = koMapping.toJS(config[key]);
                    });
                    configJSON.label = this.get('label')();
                    return configJSON;
                },
                write: function(value) {
                    if (window.location.pathname.includes(arches.urls.graph_designer(this.card.get('graph_id')))){
                        var config = this.get('config');
                        for (var key in value) {
                            if (key === 'label') {
                                this.get('label')(value[key]);
                            }
                            if (config[key]) {
                                var oldJSON = koMapping.toJSON(config[key]);
                                var newJSON = (value[key] !== null && value[key] !== undefined) ? koMapping.toJSON(value[key]) : value[key];
                                if (oldJSON !== newJSON) {
                                    koMapping.fromJSON(
                                        newJSON,
                                        config[key]
                                    );
                                }
                            }
                        }
                    }
                },
                owner: this
            });
            this.configJSON.extend({ rateLimit: { timeout: 100, method: "notifyWhenChangesStop" } });

            this.disposables.push(this.configJSON);

            this.dispose = function() {
                dispose(self);
            };

            return this;
        },

        /**
         * parse - parses the passed in attributes into a {@link CardWidgetModel}
         * @memberof CardWidgetModel.prototype
         * @param  {object} attributes - the properties to seed a {@link CardWidgetModel} with
         */
        parse: function(attributes){
            var self = this;

            _.each(attributes, function(value, key){
                if (key === 'config') {
                    if (typeof value === 'string') {
                        value = JSON.parse(value);
                    }
                    var configKeys = [];
                    _.each(value, function(configVal, configKey) {
                        if (configVal === null || configVal === undefined || !configVal.__ko_mapping__) {
                            configVal = koMapping.fromJS(configVal);
                        }
                        value[configKey] = configVal;
                        configKeys.push(configKey);
                    });
                    this.set(key, value);
                    this.configKeys = ko.observableArray(configKeys);
                } else if (key==='widget_id') {
                    var widgetId = ko.observable(value);
                    this.set(key, ko.computed({
                        read: function() {
                            return widgetId();
                        },
                        write: function(value) {
                            var key;
                            var defaultConfig = JSON.parse(widgets[value].defaultconfig);
                            for (key in defaultConfig) {
                                defaultConfig[key] = ko.observable(defaultConfig[key]);
                            }
                            var currentConfig = this.get('config');
                            this.set('config', _.defaults(currentConfig, defaultConfig));
                            for (key in defaultConfig) {
                                self.configKeys.push(key);
                            }
                            widgetId(value);
                        },
                        owner: this
                    }));
                    this.disposables.push(this.get(key));
                } else {
                    this.set(key, ko.observable(value));
                }
                this[key] = this.get(key);
            }, this);
        },


        /**
         * toJSON - casts the model as a JSON object
         * @return {object} a JSON object representation of the model
         */
        toJSON: function() {
            var ret = {};
            for (var key in this.attributes){
                if (key !== 'config') {
                    ret[key] = this.attributes[key]();
                } else {
                    ret[key] = this.configJSON();
                }
            }
            return ret;
        }
    });
});
