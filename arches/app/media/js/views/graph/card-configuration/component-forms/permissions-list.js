define([
    'knockout',
    'views/list',
    'views/graph/card-configuration/component-forms/permissions-form'
], function(ko, ListView, PermissionsForm) {
    var PermissionsList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name PermissionsList
        */

        single_select: false,

        /**
        * initializes the view with optional parameters
        * @memberof PermissionsList.prototype
        * @param {object} options
        * @param {boolean} options.permissions - a list of allowable permissions
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);
            this.card = options.card;
            this.card.subscribe(function(card){
                this.parseItems(card);
            }, this);
            this.parseItems(this.card());

            this.getPermsForDisplay = function(){
                var ret = {'default': [], 'local': []};
                this.perms.local().forEach(function(perm){
                    ret.local.push(ko.unwrap(perm.name));
                });
                this.perms.default().forEach(function(perm){
                    ret.default.push(ko.unwrap(perm.name));
                });
                return ret;
            };

            this.permissionsForm = new PermissionsForm({
                permissions: options.permissions,
                selectedItems: this.selectedItems,
                getPermsForDisplay: this.getPermsForDisplay
            })
        },

        /**
        * Parses users and groups into usable list items
        * @memberof PermissionsList.prototype
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        parseItems: function(card){
            this.items.removeAll();
            card.get('users')().forEach(function(user){
                this.items.push({'name': user.username, 'perms': user.perms, 'type': user.type})
            }, this);
            card.get('groups')().forEach(function(group){
                this.items.push({'name': group.name, 'perms': group.perms, 'type': group.type})
            }, this);
        },

        /**
        * Selects the passed in node
        * @memberof PermissionsList.prototype
        * @param {object} item - the node to be selected via {@link GraphModel#selectNode}
        * @param {object} evt - click event object
        */
        selectItem: function(item, evt){
            ListView.prototype.selectItem.apply(this, arguments);
        },

    });
    return PermissionsList;
});
