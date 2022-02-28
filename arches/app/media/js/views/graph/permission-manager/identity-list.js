define([
    'knockout',
    'views/list'
], function(ko, ListView) {
    var IdentityList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name IdentityList
        */

        singleSelect: true,

        /**
        * initializes the view with optional parameters
        * @memberof IdentityList.prototype
        * @param {object} options
        * @param {boolean} options.permissions - a list of allowable permissions
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);
            this.items = options.items;
        }

    });
    return IdentityList;
});
