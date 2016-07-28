define([
    'backbone',
    'underscore',
    'knockout',
    'widgets',
    'bindings/sortable'
], function(Backbone, _, ko, widgets) {
    var CardFormPreview = Backbone.View.extend({
        /**
        * A backbone view representing a card form preview
        * @augments Backbone.View
        * @constructor
        * @name CardFormPreview
        */

        /**
        * Initializes the view with optional parameters
        * @memberof CardFormPreview.prototype
        */
        initialize: function(options) {
            var self = this;
            this.card = options.card;
            this.selection = options.selection;
            this.widgetLookup = widgets;
            this.currentTabIndex = ko.computed(function () {
                if (!self.card.isContainer() || self.selection() === self.card) {
                    return 0;
                }
                var card = self.selection();
                if (card.node) {
                    card = card.card;
                }
                var index = self.card.get('cards')().indexOf(card);
                return index;
            });
        },

        beforeMove: function (e) {
            e.cancelDrop = (e.sourceParent!==e.targetParent);
        }
    });
    return CardFormPreview;
});
