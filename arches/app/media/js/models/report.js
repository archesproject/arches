define(['arches',
    'models/abstract',
    'models/card',
    'models/graph',
    'knockout',
    'knockout-mapping',
    'underscore'
], function(arches, AbstractModel, CardModel, GraphModel, ko, koMapping, _) {
    var ReportModel = AbstractModel.extend({
        /**
         * A backbone model to manage report data
         * @augments AbstractModel
         * @constructor
         * @name ReportModel
         */

        url: arches.urls.report_editor,

        initialize: function(options) {
            var self = this;

            var setupTiles = function(card) {
                card.tiles = _.filter(options.tiles, function(tile) {
                    return tile.nodegroup_id === card.nodegroup_id;
                });
                card.tiles.forEach(function(t1) {
                    t1.tiles = _.filter(options.tiles, function(t2) {
                        return t1.tileid === t2.parenttile_id;
                    });
                });
                card.cards.forEach(setupTiles);
            };
            options.cards.forEach(setupTiles);

            this.cards = _.map(options.cards, function(card) {
                var cardModel = new CardModel({
                    data: _.extend(card, {
                        nodes: options.graphModel.get('nodes')
                    }),
                    datatypelookup: options.graphModel.get('datatypelookup'),
                    cardComponents: options.cardComponents
                });
                return cardModel;
            });

            this.set('reportid', ko.observable());
            this.set('name', ko.observable());
            this.set('template_id', ko.observable());
            this.set('active', ko.observable());
            this.set('config', {});
            self.configKeys = ko.observableArray();

            this._data = ko.observable('{}');

            this.dirty = ko.computed(function() {
                return JSON.stringify(_.extend(JSON.parse(self._data()), self.toJSON())) !== self._data();
            });

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

            this.parse(options.report);
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
                case 'reportid':
                    this.set('id', value);
                    this.get('reportid')(value);
                    break;
                case 'name':
                case 'template_id':
                case 'graph':
                case 'active':
                    this.get(key)(value);
                    break;
                case 'config':
                    var config = {};
                    var configKeys = [];
                    self.configKeys.removeAll();
                    _.each(value, function(configVal, configKey) {
                        if (!ko.isObservable(configVal)) {
                            configVal = ko.observable(configVal);
                        }
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
            for (var key in this.attributes) {
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
