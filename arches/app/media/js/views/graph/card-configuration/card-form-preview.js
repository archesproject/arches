define([
    'backbone',
    'underscore',
    'widgets'
], function(Backbone, _, widgets) {
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

            this.widgetLookup = {};
            _.each(widgets, function (widget, id) {
                self.widgetLookup[id] = widget;
            });
        }
    });
    return CardFormPreview;
});
