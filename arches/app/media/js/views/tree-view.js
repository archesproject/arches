define([
    'jquery',
    'backbone',
    'knockout'
], function($, Backbone, ko) {
    var TreeView = Backbone.View.extend({
        /**
        * A base view to manage lists of things
        * @augments Backbone.View
        * @constructor
        * @name TreeView
        */

        /**
        * the list of items being managed
        * @type {array}
        * @memberof TreeView.prototype
        */
        items: ko.observableArray(),

        /**
        * if true then only allow 1 selected item at a time
        * @type {boolean}
        * @memberof TreeView.prototype
        */
        single_select: true,

        /**
        * Callback function called every time a user types into the filter input box
        * @memberof TreeView.prototype
        */
        filter_function: function(item){
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
        * @memberof TreeView.prototype
        * @param {object} options - optional parameters to pass in during initialization
        */
        initialize: function(options) {
            var self = this;

            if (options.items && !this.items) {
                this.items = options.items;
            }
            this.tree = this.constructTree(this.items);

            var initializeItem = function(item){
                if (!item.filtered) {
                    item.filtered = ko.observable(false);
                }
                if (!('selectable' in item)){
                    item.selectable = true;
                }
                if (!item.selected) {
                    item.selected = ko.observable(false);
                }
                if (!item.expanded) {
                    item.expanded = ko.observable(false);
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

        constructTree: function(ar){
            var lut = {},sorted = [];
            function sort(a){
                var len = a.length,
                    fix = -1;
                for (var i = 0; i < len; i++ ){
                  while (!!~(fix = a.findIndex(e => a[i].parent == e.id)) && fix > i)
                        [a[i],a[fix]] = [a[fix],a[i]]; // ES6 swap
                  lut[a[i].id]=i;
                }
                //console.log(lut); //check LUT on the console.
                return a;
            }
            sorted = sort(ar.slice(0)); // don't modify things that don't belong to you :)
            for (var i = sorted.length-1; i >= 0; i--){
                if (sorted[i].parent != "#") {
                    !!sorted[lut[sorted[i].parent]].children && 
                    sorted[lut[sorted[i].parent]].children.push(sorted.splice(i,1)[0])
                    || (sorted[lut[sorted[i].parent]].children = [sorted.splice(i,1)[0]]);
                }
            }
          return sorted;
        },

        /**
        * Toggles the selected status of a single list item, if {@link TreeView#single_select} is
        *   true clear the selected status of all other list items
        * @memberof TreeView.prototype
        * @param {object} item - the item to be selected or unselected
        * @param {object} evt - click event object
        */
        selectItem: function(item, evt){
            if(!!item.selectable){
                var selectedStatus = item.selected();
                if(this.single_select){
                    this.clearSelection();
                }
                item.selected(!selectedStatus);
                this.trigger('item-clicked', item, evt);
            }
        },

        /**
        * Unselect all items in the list
        * @memberof TreeView.prototype
        */
        clearSelection: function(){
            this.items().forEach(function(item){
                item.selected(false);
            }, this);
        },

        /**
        * Reset the search string to blank
        * @memberof TreeView.prototype
        */
        clearSearch: function(){
            this.filter('');
        },

        /**
        * Reset the search string to blank
        * @memberof TreeView.prototype
        */
        expandAll: function(){
            this.items().forEach(function(item){
                item.expanded(true);
            }, this);
        },

        /**
        * Reset the search string to blank
        * @memberof TreeView.prototype
        */
        collapseAll: function(){
            this.items().forEach(function(item){
                item.expanded(false);
            }, this);
        },
    });

    return TreeView;
});
