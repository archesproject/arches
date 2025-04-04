import $ from 'jquery';
import Backbone from 'backbone';
import ko from 'knockout';
import ListView from 'views/list';


var TreeView = ListView.extend({
    /**
    * A list view to manage a hierarchical lists of things
    * @augments ListView
    * @constructor
    * @name TreeView
    */

    /**
    * Used internally to add observable parameters to list items
    * @memberof TreeView.prototype
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
        if (!item.expanded) {
            item.expanded = ko.observable(false);
        }
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

export default TreeView;
