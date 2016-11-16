define([
    'backbone',
    'knockout',
], function(Backbone, ko) {
    var PermissionsForm = Backbone.View.extend({
        /**
        * initializes the view with optional parameters
        * @memberof PermissionsForm.prototype
        * @param {object} options
        * @param {boolean} options.permissions - a list of allowable permissions
        * @param {boolean} options.selectedItems - a reference to the selected items in the {@link PermissionsList}
        */
        initialize: function(options) {
            this.permissions = options.permissions;
            this.selectedItems = options.selectedItems;
            this.selectedPermissions = ko.observableArray();
            this.getPermsForDisplay = options.getPermsForDisplay;
        },

        /**
        * Closes the form and deselects the currently selected items
        * @memberof PermissionsForm.prototype
        */
        close: function(){
            this.selectedItems().forEach(function(item){
                item.selected(false);
            }, this);
        },

        /**
        * Associates the selected permissions with the selected users/groups
        * @memberof PermissionsForm.prototype
        */
        applyPermissions: function(){
            this.resetPermissions();
            this.selectedItems().forEach(function(item){
                this.selectedPermissions().forEach(function(perm){
                    item.perms.local.push(perm);
                }, this);
            }, this);
        },

        /**
        * Resets the permissions associated with the selected users/groups 
        * back to their default state
        * @memberof PermissionsForm.prototype
        */
        resetPermissions: function(){
            this.selectedItems().forEach(function(item){
                item.perms.local.removeAll();
            }, this);
        }


    });
    return PermissionsForm;
});
