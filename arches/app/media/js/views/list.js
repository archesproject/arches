define([
    'jquery',
    'backbone',
    'knockout'
], function($, Backbone, ko) {
    var ListView = Backbone.View.extend({
        /**
        * A base view to manage lists of things
        * @augments Backbone.View
        * @constructor
        * @name ListView
        */

        /**
        * the list of items being managed
        * @type {array}
        * @memberof ListView.prototype
        */
        items: ko.observableArray(),

        /**
        * if true then only allow 1 selected item at a time
        * @type {boolean}
        * @memberof ListView.prototype
        */
        single_select: true,

        /**
        * Callback function called every time a user types into the filter input box
        * @memberof ListView.prototype
        */
        filter_function: function(newValue){
            var filter = this.filter().toLowerCase();
            this.items().forEach(function(item){
                var name = typeof item.name === 'string' ? item.name : item.name();
                item.filtered(true);
                if(name.toLowerCase().indexOf(filter) !== -1){
                    item.filtered(false);
                }
            }, this);
        },

        /**
        * @memberof ListView.prototype
        */
        initialize: function(options) {
            this.filter = ko.observable('');
            this.filter.subscribe(this.filter_function, this, 'change');
        },

        /**
        * Toggles the selected status of a single list item, if {@link ListView#single_select} is 
        *   true clear the selected status of all other list items
        * @memberof ListView.prototype
        */
        selectItem: function(item, evt){
            if(this.trigger('item-selected', item, evt)){
                var selectedStatus = item.selected();
                if(this.single_select){
                    this.clearSelection();
                }
                item.selected(!selectedStatus);
            }
        },

        /**
        * Unselect all items in the list
        * @memberof ListView.prototype
        */
        clearSelection: function(){
            this.items().forEach(function(item){
                item.selected(false);
            }, this);
        },

        /**
        * Reset the search string to blank
        * @memberof ListView.prototype
        */
        clearSearch: function(){
            this.filter('');
        }
    });

    return ListView;
});
