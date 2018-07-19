define([
    'backbone',
    'knockout',
    'views/list'
], function(Backbone, ko, ListView) {
    var GroupedNodeList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name GroupedNodeList
        */

        singleSelect: false,

        /**
        * Callback function called every time a user types into the filter input box
        * @memberof ListView.prototype
        */
        filterFunction: function(){
            // first run the standard filter
            ListView.prototype.filterFunction.apply(this, arguments);

            // next bring back and any card containers that were filtered that have children that were not
            this.items().forEach(function(item){
                if (item.type === 'card_container'){
                    item.children.forEach(function(childItem){
                        if (!childItem.filtered()){
                            item.filtered(false);
                        }
                    });
                }
            }, this);
        },

        /**
        * initializes the view with optional parameters
        * @memberof GroupedNodeList.prototype
        * @param {object} options
        * @param {boolean} options.cards - a hierarchical list of all cards (simplified json) for a resource model
        * @param {boolean} options.datatypes - a list of all datatypes
        */
        initialize: function(options) {

            this.outerCards = options.cards.children;

            var parseData = function(item){
                if (item.type === 'card' || item.type === 'card_container'){
                    this.items.push(item);
                    item.visible = ko.observable(item.type === 'card_container');
                }else{
                    item.selectable = false;
                    item.active = ko.observable(false);
                    item.filtered = ko.observable(false);
                }
                item.children.forEach(parseData, this);
                item.children.sort(function(a, b) {
                    return ko.unwrap(a.name).localeCompare(ko.unwrap(b.name));
                });
            };

            parseData.call(this, options.cards);

            this.datatypes = {};
            options.datatypes.forEach(function(datatype){
                this.datatypes[datatype.datatype] = datatype.iconclass;
            }, this);

            this.showNodes = ko.observable(false);
            this.showNodes.subscribe(function(show){
                this.items().forEach(function(item){
                    if(item.type === 'card'){
                        item.visible(show);
                    }
                });
            }, this);

            ListView.prototype.initialize.apply(this, arguments);
        },

        /**
        * Toggles the selected status of a single list item, if {@link ListView#singleSelect} is
        *   true clear the selected status of all other list items
        * @memberof ListView.prototype
        * @param {object} item - the item to be selected or unselected
        * @param {object} evt - click event object
        */
        selectItem: function(item, evt, parentItem){
            var self = this;
            if(!!item.selectable){
                var selectedStatus = item.selected();
                if(this.singleSelect){
                    this.clearSelection();
                }
                item.selected(parentItem ? parentItem.selected() : !selectedStatus);
                this.trigger('item-clicked', item, evt);
                item.children.forEach(function(childItem){
                    self.selectItem(childItem, evt, item);
                });
            }else{
                if (parentItem){
                    item.active(parentItem.selected());
                }
            }
        },

        /**
        * Unselect all items in the list
        * @memberof ListView.prototype
        */
        clearSelection: function(){
            this.items().forEach(function(item){
                item.selected(false);
                item.children.forEach(function(child) {
                    if (child.type === 'node') {
                        child.active(false);
                    }
                });
            }, this);
        },

        /**
        * Toggles hidden nodes in the list
        * @memberof ListView.prototype
        * @param {object} item - the item to be hidden or shown
        * @param {object} evt - click event object
        */
        toggleNodes: function(item, evt){
            item.visible(!item.visible());
            evt.stopPropagation();
        }

    });
    return GroupedNodeList;
});
