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
        }

    });
    return NodeList;
});
