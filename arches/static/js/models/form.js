define([
    'arches',
    'models/abstract',
    'knockout',
    'knockout-mapping',
    'underscore'
], function (arches, AbstractModel, ko, koMapping, _) {

    var FormModel = AbstractModel.extend({
        /**
        * A backbone model to manage form data
        * @augments AbstractModel
        * @constructor
        * @name FormModel
        */
        url: arches.urls.form,

        /**
        * parse - parses the passed in attributes into a {@link FormModel}
        * @memberof FormModel.prototype
        * @param  {object} attributes - the properties to seed a {@link FormModel} with
        */
        initialize: function(options) {
            var self = this;
            this.formid = options.data.formid;
            this._json = ko.observable('');
            this.iconclass = ko.observable();
            this.title = ko.observable();
            this.subtitle = ko.observable();
            this.visible = ko.observable();
            this.cards = ko.observableArray();
            this.availableCards = ko.observableArray();
            this._cards = options.cards;

            options.data.cards = _.map(options.forms_x_cards, function (formXCard) {
                return _.find(options.cards, function(card) {
                    return card.cardid === formXCard.card_id;
                });
            });

            this.parse(options.data);

            this.json = ko.computed(function() {
                return JSON.stringify(_.extend(JSON.parse(self._json()), {
                    iconclass: self.iconclass(),
                    title: self.title(),
                    subtitle: self.subtitle(),
                    visible: self.visible(),
                    cards: self.cards()
                }))
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._json();
            });
        },

        parse: function(data) {
            var self = this;

            this.formid = data.formid;
            this._json(JSON.stringify(data));

            this.iconclass(data.iconclass);
            this.title(data.title);
            this.subtitle(data.subtitle);
            this.visible(data.visible);
            this.cards(data.cards);

            var addedCardIds = _.map(this.cards(), function (card) {
                return card.cardid;
            });
            this.availableCards.removeAll();
            _.each(this._cards, function (card) {
                if (!_.contains(addedCardIds, card.cardid)) {
                    self.availableCards.push(card);
                }
            });

            this.set('id', data.formid)
        },

        /**
        * discards unsaved model changes and resets the model data
        * @memberof FormModel.prototype
        */
        reset: function () {
            this.parse(JSON.parse(this._json()), self);
        },

        /**
        * returns a JSON object containing model data
        * @memberof FormModel.prototype
        * @return {object} a JSON object containing model data
        */
        toJSON: function () {
            return JSON.parse(this.json());
        },
    });
    return FormModel;
});
