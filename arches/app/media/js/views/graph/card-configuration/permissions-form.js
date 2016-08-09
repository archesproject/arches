define([
    'backbone',
    'knockout',
], function(Backbone, ko) {
    var PermissionsForm = Backbone.View.extend({
        /**
        * initializes the view with optional parameters
        * @memberof PermissionsList.prototype
        * @param {object} options
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            this.permissions = options.permissions;
            this.showing = ko.observable(false);
        },

        /**
        * Closes the form and deselects the currently selected branch
        * @memberof BranchList.prototype
        */
        close: function(){
            this.showing(false);
        },

    });
    return PermissionsForm;
});
