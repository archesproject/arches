define([
    'backbone',
    'knockout',
    'bindings/summernote'
], function(Backbone,  ko) {
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
            var self = this;
            this.card = options.card;
            this.selection = options.selection || ko.observable(this.card);
            this.helpPreviewActive = options.helpPreviewActive || ko.observable(false);
            this.helpTabActive = ko.observable(false);
            this.selection.subscribe(function () {
                self.helpTabActive(false);
                self.helpPreviewActive(false);
            })
        }
    });
    return CardComponentForm;
});
