define([
    'knockout',
    'underscore',
    'arches',
    'views/list'
], function(ko, _, arches, ListView) {
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
            this.selectedIndex = ko.observable(0);
            this.hideIdentityDetails = ko.observable(false);
            ListView.prototype.initialize.apply(this, arguments);
            var self = this;
            this.items = options.items;
            _.each(this.items(), function(item){
                item.approved = ko.observable(false);
            })
            this.usersGroups = ko.observableArray()
            this.selected = ko.computed(function(){
                var res = self.selectedItems().length > 0 ? self.selectedItems()[0] : '';
                return res;
            })
            this.filteredItems = ko.computed(function(){
                var filtered = _.filter(self.items(), function(item){return !item.filtered()});
                self.selectedIndex(_.indexOf(filtered, self.selected()));
                self.hideIdentityDetails(!_.contains(filtered, self.selected())) //If the selected item is filtered out, we need to hide its cards
                return filtered;
            })
        }


    });
    return IdentityList;
});
