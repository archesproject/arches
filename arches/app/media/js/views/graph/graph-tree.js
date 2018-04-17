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
            this.tree = this.construct(this.items);
            ListView.prototype.initialize.apply(this, arguments);
        },

        construct: function(ar){
            var lut = {},sorted = [];
            function sort(a){
                var len = a.length,
                    fix = -1;
                for (var i = 0; i < len; i++ ){
                  while (!!~(fix = a.findIndex(e => a[i].parent == e.id)) && fix > i)
                        [a[i],a[fix]] = [a[fix],a[i]]; // ES6 swap
                  lut[a[i].id]=i;
                }
                console.log(lut); //check LUT on the console.
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

        expand_node: function(e, node){
            node.expanded = true;
        },

        /**
        * Selects the passed in node
        * @memberof NodeList.prototype
        * @param {object} item - the node to be selected via {@link GraphModel#selectNode}
        * @param {object} evt - click event object
        */
        selectItem: function(item, evt){
            this.graphModel.selectNode(item);
            this.trigger('node-selected', item);
        },

    });
    return NodeList;
});
