define([
    'views/list'
], function(ListView) {
    var NodeList = ListView.extend({

        single_select: true,

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
