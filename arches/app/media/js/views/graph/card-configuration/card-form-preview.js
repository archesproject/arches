define([
    'backbone'
], function(Backbone) {
    var CardFormPreview = Backbone.View.extend({
        /**``
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
            this.card = options.card;
        }
    });
    return CardFormPreview;
});
