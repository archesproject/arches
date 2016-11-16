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

            var forms = [];
            options.forms.forEach(function(formData) {
                form = _.clone(formData);
                form.cards = [];
                options.forms_x_cards.forEach(function(form_x_card) {
                    if (form_x_card.form_id === form.formid) {
                        var card = _.find(options.cards, function(card) {
                            return card.cardid === form_x_card.card_id;
                        });
                        var cardModel = new CardModel({
                            data: card,
                            datatypes: options.datatypes
                        });
                        cardModel.formId = form.formid;
                        form.cards.push(cardModel);
                    }
                })
                form.sortorder = Infinity;
                form.active = ko.observable(true);
                form.label = ko.observable(form.title);
                forms.push(form);
            });
            this.forms = ko.observableArray(forms);
            this.activeForms = ko.computed(function() {
                return _.filter(self.forms(), function(form) {
                    return form.active();
                });
            });
            this.graph = new GraphModel({data: options.graph});

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
                read: function () {
                    var configJSON = {};
                    var config = this.get('config');
                    _.each(this.configKeys(), function(key) {
                        configJSON[key] = ko.unwrap(config[key]);
                    });
                    return configJSON;
                },
                write: function (value) {
                    var config = this.get('config');
                    for (key in value) {
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

            var parseCardConfig = function(cardId, cardConfig, cards) {
                var card = _.find(cards, function(card) {
                    return card.get('id') === cardId;
                });
                if (card) {
                    card.get('name')(cardConfig.label);
                    _.each(cardConfig.nodes, function(nodeConfig, nodeId) {
                        var widget = _.find(card.get('widgets')(), function(widget) {
                            return widget.node.nodeid === nodeId;
                        });
                        widget.get('label')(nodeConfig.label);
                    });
                    _.each(cardConfig.cards, function(cardConfig, cardId) {
                        parseCardConfig(cardId, cardConfig, card.get('cards')());
                    });
                }
            }

            _.each(attributes, function(value, key) {
                switch (key) {
                    case 'reportid':
                        this.set('id', value);
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
                    case 'formsconfig':
                        var forms = self.forms();
                        _.each(value, function(formconfig, formid) {
                            var form = _.find(forms, function(form) {
                                return form.formid === formid;
                            });
                            if (form) {
                                _.extend(form, _.pick(formconfig, 'sortorder'));
                                form.active(formconfig.active);
                                form.label(formconfig.label);
                                _.each(formconfig.cards, function(cardConfig, cardId) {
                                    parseCardConfig(cardId, cardConfig, form.cards);
                                })
                            }
                        });
                    default:
                        this.set(key, value);
                }
            }, this);

            this.forms.sort(function(f1, f2) {
                return f1.sortorder > f2.sortorder;
            });

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
            ret.formsconfig = {};
            var getCardConfig = function(card) {
                var cards = card.get('cards')();
                var widgets = card.get('widgets')();
                var cardsConfig = {};
                var nodesConfig = {};
                cards.forEach(function(childCard) {
                    cardsConfig[childCard.get('id')] = getCardConfig(childCard);
                });
                widgets.forEach(function(widget) {
                    nodesConfig[widget.node.nodeid] = {
                        label: widget.get('label')()
                    };
                });
                return {
                    label: card.get('name')(),
                    cards: cardsConfig,
                    nodes: nodesConfig
                };
            }
            this.forms().forEach(function(form, i) {
                var cardsConfig = {};
                form.cards.forEach(function(card) {
                    cardsConfig[card.get('id')] = getCardConfig(card);
                })
                ret.formsconfig[form.formid] = {
                    sortorder: i,
                    active: form.active(),
                    label: form.label(),
                    cards: cardsConfig
                };
            });
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
