define([
    'views/list'
], function(ListView) {
    var NodeList = ListView.extend({

        single_select: true,
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
            this.graphModel = options.graphModel;
        },

        selectItem: function(item, evt){
            this.trigger('node-clicked', item);
            if (item.editing()) {
                ListView.prototype.selectItem.apply(this, arguments);
            }
        },

        clearSelection: function(){
            ListView.prototype.clearSelection.apply(this, arguments);
        },

    });
    return NodeList;
});
