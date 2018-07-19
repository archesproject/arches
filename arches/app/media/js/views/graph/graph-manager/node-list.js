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

        filterFunction: function(){
            var filter = this.filter().toLowerCase();
            this.items().forEach(function(item){
                item.filtered(true);
                if(item.name().toLowerCase().indexOf(filter) !== -1 ||
                    item.datatype().toLowerCase().indexOf(filter) !== -1 ||
                    item.ontologyclass().toLowerCase().indexOf(filter) !== -1){
                    item.filtered(false);
                }
            }, this);
        },

        /**
        * initializes the view with optional parameters
        * @memberof NodeList.prototype
        * @param {object} options
        * @param {boolean} options.graphModel - a reference to the selected {@link GraphModel}
        */
        initialize: function(options) {
            this.graphModel = options.graphModel;
            this.items = options.graphModel.get('nodes');
            ListView.prototype.initialize.apply(this, arguments);
        },

        /**
        * Selects the passed in node
        * @memberof NodeList.prototype
        * @param {object} item - the node to be selected via {@link GraphModel#selectNode}
        * @param {object} evt - click event object
        */
        selectItem: function(item){
            this.graphModel.selectNode(item);
            this.trigger('node-selected', item);
        },

    });
    return NodeList;
});
