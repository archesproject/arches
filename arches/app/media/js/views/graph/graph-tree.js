define([
    'knockout',
    'views/tree-view'
], function(ko, TreeView) {
    var GraphTree = TreeView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments TreeView
        * @constructor
        * @name GraphTree
        */

        filter_function: function(newValue){
            var filter = this.filter().toLowerCase();
            this.items().forEach(function(item){
                item.filtered(true);
                if (item.name().toLowerCase().indexOf(filter) !== -1 ||
                    item.datatype().toLowerCase().indexOf(filter) !== -1 ||
                    (!!(item.ontologyclass()) ? item.ontologyclass().toLowerCase().indexOf(filter) !== -1 : false)){
                    item.filtered(false);
                }
            }, this);
        },

        /**
        * initializes the view with optional parameters
        * @memberof GraphTree.prototype
        * @param {object} options
        * @param {boolean} options.graphModel - a reference to the selected {@link GraphModel}
        */
        initialize: function(options) {
            this.graphModel = options.graphModel;
            this.items = this.graphModel.get('nodes');
            TreeView.prototype.initialize.apply(this, arguments);
        },

        /**
        * Selects the passed in node
        * @memberof GraphTree.prototype
        * @param {object} item - the node to be selected via {@link GraphModel#selectNode}
        * @param {object} e - click event object
        */
        selectItem: function(item, e){
            this.graphModel.selectNode(item);
            this.trigger('node-selected', item);
        },

        addChildNode: function(item, e) {
            e.stopImmediatePropagation();
            console.log(item);
        },

        deleteNode: function(item, e) {
            e.stopImmediatePropagation();
            var parentNode = this.graphModel.getParentNode(item);
            this.graphModel.deleteNode(item, function(response, status){
                if(status === 'success') {
                    parentNode.children.remove(item);
                }else{
                    this.trigger('error', response.responseJSON);
                }
            }, this);
        }

    });
    return GraphTree;
});
