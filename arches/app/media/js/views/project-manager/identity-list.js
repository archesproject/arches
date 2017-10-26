define([
    'knockout',
    'arches',
    'views/list'
], function(ko, arches, ListView) {
    var IdentityList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name IdentityList
        */

        single_select: true,

        /**
        * initializes the view with optional parameters
        * @memberof IdentityList.prototype
        * @param {object} options
        * @param {boolean} options.permissions - a list of allowable permissions
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);
            var self = this;
            this.items = options.items;
            _.each(this.items(), function(item){
                item.approved = ko.observable(false);
            })
            this.groupUsers = ko.observableArray()
            this.usersGroups = ko.observableArray()
            this.getGroupUsers = function(identity) {
                $.ajax({
                    url: arches.urls.group_users,
                    data: {type: identity.type, id: identity.id},
                    type: 'json',
                    method: 'POST'
                }).done(function(data) {
                    self.groupUsers(data)
                    var usersGroups = _.filter(self.items(), function(item){
                        if (item.type === 'group' && _.contains(self.selected().group_ids, item.id)) {
                            return item
                        }
                    })
                    self.usersGroups(usersGroups);
                }).fail(function(err) {
                    console.log(err);
                })
            };

            this.selected = ko.computed(function(){
                var res = self.selectedItems().length > 0 ? self.selectedItems()[0] : '';
                if (res != '') {
                    self.getGroupUsers(res);
                }
                return res;
            })
        }

    });
    return IdentityList;
});
