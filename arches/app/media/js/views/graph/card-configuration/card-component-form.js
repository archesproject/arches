define([
    'backbone',
    'bindings/summernote'
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
            this.selection = options.selection;
        }
    });
    return CardComponentForm;
});
