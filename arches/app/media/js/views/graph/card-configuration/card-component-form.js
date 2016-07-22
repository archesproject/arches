define([
    'backbone'
], function(Backbone) {
    var CardComponentForm = Backbone.View.extend({
        /**
        * A backbone view representing a card component form
        * @augments Backbone.View
        * @constructor
        * @name CardComponentForm
        */

        /**
        * Initializes the view with optional parameters
        * @memberof CardComponentForm.prototype
        */
        initialize: function(options) {
            this.card = options.card;
        }
    });
    return CardComponentForm;
});
