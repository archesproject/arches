define([
    'backbone',
    'knockout',
    'views/graph/card-configuration/component-forms/permissions-list',
    'bindings/summernote'
], function(Backbone,  ko, PermissionsList) {
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
        * @param {boolean} options.selection - the selected item, either a {@link CardModel} or a {@link NodeModel}
        */
        initialize: function(options) {
            //this.card = options.card;
            this.selection = options.selection;
            this.card = ko.observable();
            this.node = ko.observable();
            
            this.updateSelection = function(selection) {
                if('isContainer' in selection){
                    this.card(selection);
                }
                if('node' in selection){
                    this.node(selection);
                }
            };

            this.helpPreviewActive = ko.observable(false);
            this.helpTabActive = ko.observable(false);
            this.selection.subscribe(function (selection) {
                this.helpTabActive(false);
                this.helpPreviewActive(false);
                this.updateSelection(selection);
            }, this);

            this.updateSelection(this.selection());

            this.permissionsList = new PermissionsList({
                card: this.card,
                permissions: options.permissions
            });

        }
    });
    return CardComponentForm;
});
