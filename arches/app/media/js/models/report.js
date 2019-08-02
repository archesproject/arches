define(['arches',
    'models/abstract',
    'knockout',
    'knockout-mapping',
    'underscore',
    'report-templates'
], function(arches, AbstractModel, ko, koMapping, _, reportLookup) {
    var ReportModel = AbstractModel.extend({
        /**
         * A backbone model to manage report data
         * @augments AbstractModel
         * @constructor
         * @name ReportModel
         */

        url: arches.urls.graph,

        initialize: function(options) {
            var self = this;
            this.templateId = ko.observable(self.get('graph').template_id);
            this.cards = options.cards || [];
            this.preview = options.preview;
            this.userisreviewer = options.userisreviewer;

            this.set('graphid', ko.observable());
            this.set('config', {});
            self.configKeys = ko.observableArray();

            this._data = ko.observable('{}');

            this.configJSON = ko.observable({});
            this.configState = {};
            this.configKeys.subscribe(function(val){
                var config;
                self.defaultConfig = JSON.parse(reportLookup[self.templateId()].defaultconfig);
                if (val.length) {
                    self.configState = {};
                    config = self.get('config');
                    _.each(val, function(key) {
                        if (self.defaultConfig.hasOwnProperty(key)) {
                            self.configState[key] = ko.unwrap(config[key]);
                        }
                    });
                    self.configState = koMapping.fromJS(self.configState);
                }
            });

            this.resetConfigs = function(previousConfigs) {
                this.configKeys().forEach(function(key){
                    if (self.defaultConfig.hasOwnProperty(key)) {
                        if (JSON.stringify(self.configState[key]()) !== JSON.stringify(previousConfigs[key])) {
                            koMapping.fromJS(previousConfigs, self.configState);
                        }
                    }
                });
            };

            this.graph = options.graph;
            this.parse(options.graph);
        },

        /**
         * parse - parses the passed in attributes into a {@link ReportModel}
         * @memberof ReportModel.prototype
         * @param  {object} attributes - the properties to seed a {@link ReportModel} with
         */
        parse: function(attributes) {
            var self = this;
            this._attributes = attributes;

            _.each(attributes, function(value, key) {
                switch (key) {
                case 'graphid':
                    this.set('id', value);
                    this.get('graphid')(value);
                    break;
                case 'template_id':
                    self.templateId(value);
                    this.set(key, ko.computed({
                        read: function() {
                            return self.templateId();
                        },
                        write: function(value) {
                            var key;
                            var configKeys = [];
                            var defaultConfig = JSON.parse(reportLookup[value].defaultconfig);
                            for (key in defaultConfig) {
                                defaultConfig[key] = ko.observable(defaultConfig[key]);
                            }
                            var currentConfig = this.get('config');
                            this.set('config', _.defaults(currentConfig, defaultConfig));
                            for (key in defaultConfig) {
                                if (_.contains(self.configKeys(), key) === false) {
                                    configKeys.push(key);
                                }
                            }
                            self.templateId(value);
                            self.configKeys(self.configKeys().concat(configKeys));
                        },
                        owner: this
                    }));
                    break;
                case 'config':
                    var config = {};
                    var configKeys = [];
                    self.configKeys.removeAll();
                    _.each(value, function(configVal, configKey) {
                        config[configKey] = configVal;
                        configKeys.push(configKey);
                    });
                    this.set(key, config);
                    self.configKeys(configKeys);
                    break;
                default:
                    this.set(key, value);
                }
            }, this);

            this.related_resources = [];

            this.sort_related = function(anArray, property) {
                anArray.sort(function(a, b){
                    if (a[property] > b[property]) return 1;
                    if (b[property] > a[property]) return -1;
                    return 0;
                });
            };
            _.each(this.get('related_resources'), function(rr){
                var res = {'graph_name': rr.name, 'related':[]};
                _.each(rr.resources, function(resource) {
                    _.each(resource.relationships, function(relationship){
                        res.related.push({'displayname':resource.displayname,'link': arches.urls.resource_report + resource.instance_id, 'relationship': relationship});
                    });
                });
                this.sort_related(res.related, 'displayname');
                this.related_resources.push(res);
            }, this);

            this.sort_related(this.related_resources, 'graph_name');

            this._data(JSON.stringify(this.toJSON()));
        },

        reset: function() {
            this._attributes = JSON.parse(this._data());
            this.parse(this._attributes);
        },

        toJSON: function() {
            var ret = {};
            var self = this;
            for (var key in ['template_id', 'config']) {
                if (ko.isObservable(this.attributes[key])) {
                    ret[key] = this.attributes[key]();
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
                } else {
                    ret[key] = this.attributes[key];
                }
            }
            return ret;
        },

        save: function() {
            AbstractModel.prototype.save.call(this, function(request, status, self) {
                if (status === 'success') {
                    this._data(JSON.stringify(this.toJSON()));
                }
            }, this);
        }
    });
    return ReportModel;
});
