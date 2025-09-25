import $ from 'jquery';
import Backbone from 'backbone';
import ko from 'knockout';


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
    singleSelect: true,

    /**
    * Callback function called every time a user types into the filter input box
    * @memberof ListView.prototype
    */
    filterFunction: function(){
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
        if (options.items) {
            this.items = options.items;
        }
        if (options.items) {
            this.groups = options.groups;
        }
        this.items.subscribe(function(items) {
            items.forEach(this._initializeItem, this);
        }, this);
        if(this.filterFunction){
            this.filter = ko.observable('');
            ko.computed(function() {
                return this.filter();
            }, this).extend({
                throttle: 100
            }).subscribe(
                this.filterFunction,
                this,
                'change'
            );
            this.filterFunction();
        }

        this.selectedItems = ko.computed(function(){
            return this.items().filter(function(item){
                this._initializeItem(item);
                return item.selected();
            }, this);
        }, this);
    },

    /**
    * Used internally to add observable parameters to list items
    * @memberof ListView.prototype
    * @param {object} item - a list item
    */
    _initializeItem: function(item){
        if (!item.filtered) {
            item.filtered = ko.observable(false);
        }
        if (!('selectable' in item)){
            item.selectable = true;
        }
        if (!item.selected) {
            item.selected = ko.observable(false);
        }
    },

    /**
    * Toggles the selected status of a single list item, if {@link ListView#singleSelect} is
    *   true clear the selected status of all other list items
    * @memberof ListView.prototype
    * @param {object} item - the item to be selected or unselected
    * @param {object} evt - click event object
    */
    selectItem: function(item, evt){
        if(!!item.selectable){
            var selectedStatus = item.selected();
            if(this.singleSelect){
                this.clearSelection();
            }
            item.selected(!selectedStatus);
            this.trigger('item-clicked', item, evt);
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

export default ListView;
