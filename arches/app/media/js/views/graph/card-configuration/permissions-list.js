define([
    'views/list'
], function(ListView) {
    var PermissionsList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name NodeList
        */

        single_select: false,

        /**
        * initializes the view with optional parameters
        * @memberof PermissionsList.prototype
        * @param {object} options
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            this.card = options.card;
            this.card.get('users').forEach(function(user){
                this.items.push({'name': user.username, 'perms': user.perms, 'type': user.type})
            }, this);
            this.card.get('groups').forEach(function(group){
                this.items.push({'name': group.name, 'perms': group.perms, 'type': group.type})
            }, this);
            ListView.prototype.initialize.apply(this, arguments);
        },

        /**
        * Selects the passed in node
        * @memberof PermissionsList.prototype
        * @param {object} item - the node to be selected via {@link GraphModel#selectNode}
        * @param {object} evt - click event object
        */
        // selectItem: function(item, evt){
           
        // },

    });
    return PermissionsList;
});
