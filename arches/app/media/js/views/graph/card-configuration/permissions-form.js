define([
    'backbone'
], function(Backbone) {
    var PermissionsForm = Backbone.View.extend({
        /**
        * initializes the view with optional parameters
        * @memberof PermissionsList.prototype
        * @param {object} options
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            this.permissions = options.permissions;
        }
    });
    return PermissionsForm;
});
