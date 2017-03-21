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
                if (!item.filtered) {
                    item.filtered = ko.observable();
                }
                item.filtered(true);
                if(name.toLowerCase().indexOf(filter) !== -1){
                    item.filtered(false);
                }
            }, this);
        },

        /**
        * initializes the view with optional parameters
        * @memberof ListView.prototype
        * @param {object} options - optional parameters to pass in during initialization
        */
        initialize: function(options) {
            var self = this;
            if (options.items) {
                this.items = options.items;
            }
            if (options.items) {
                this.groups = options.groups;
            }
            var initializeItem = function(item){
                if (!item.filtered) {
                    item.filtered = ko.observable(false);
                }
                if (!item.selected) {
                    item.selected = ko.observable(false);
                }
            }
            this.items.subscribe(function (items) {
                items.forEach(initializeItem, this);
            }, this);
            if(this.filter_function){
                this.filter = ko.observable('');
                this.filter.subscribe(this.filter_function, this, 'change');
                this.filter_function();
            }

            this.selectedItems = ko.computed(function(){
                return this.items().filter(function(item){
                    initializeItem(item);
                    return item.selected();
                }, this);
            }, this);
        },

        /**
        * Toggles the selected status of a single list item, if {@link ListView#single_select} is
        *   true clear the selected status of all other list items
        * @memberof ListView.prototype
        * @param {object} item - the item to be selected or unselected
        * @param {object} evt - click event object
        */
        selectItem: function(item, evt){
            var selectedStatus = item.selected();
            if(this.single_select){
                this.clearSelection();
            }
            item.selected(!selectedStatus);
            this.trigger('item-clicked', item, evt);
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
