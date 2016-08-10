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

            this.getPermsForDisplay = function(){
                var ret = [];
                this.perms().forEach(function(perm){
                    ret.push(ko.unwrap(perm.name));
                }); 
                return ret; 
            };
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

        applyPermissions: function(){
            this.selectedItems().forEach(function(item){
                item.perms.removeAll();
                this.selectedPermissions().forEach(function(perm){
                    item.perms.push(perm);
                }, this);
            }, this);
        }

    });
    return PermissionsForm;
});
