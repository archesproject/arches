define([
    'backbone',
    'views/graph/card-configuration/permissions-list'
], function(Backbone, PermissionsList) {
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
            //this.card = options.card;
            this.selection = options.selection;

            this.updateSelection = function(selection) {
                if('isContainer' in selection){
                    this.card = selection;
                }
                if('node' in selection){
                    this.node = selection;
                }
            }
            this.selection.subscribe(function(selection){
                this.updateSelection(selection);
            }, this);

            this.updateSelection(this.selection());

            this.permissionsList = new PermissionsList({
                card: this.card
            });
        }
    });
    return CardComponentForm;
});
