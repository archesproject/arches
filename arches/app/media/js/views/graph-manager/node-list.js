define([
    'views/list'
], function(ListView) {
    var NodeList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name NodeList
        */

        filter_function: function(newValue){
            var filter = this.filter().toLowerCase();
            this.items().forEach(function(item){
                item.filtered(true);
                if(item.name().toLowerCase().indexOf(filter) !== -1 ||
                   item.datatype().toLowerCase().indexOf(filter) !== -1 ||
                   item.ontologyclass.toLowerCase().indexOf(filter) !== -1){
                    item.filtered(false);
                }
            }, this);
        },

        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);
            this.items = options.graphModel.get('nodes');
        },


        selectItem: function(item, evt){
            ListView.prototype.selectItem.apply(this, arguments);
            item.editing(!item.editing());
        },

        clearSelection: function(){
            ListView.prototype.clearSelection.apply(this, arguments);
            this.items().forEach(function(item){
                item.editing(false);
            }, this);
        },

    });
    return NodeList;
});
