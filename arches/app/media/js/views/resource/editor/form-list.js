define([
    'views/list'
], function(ListView) {
    var FormList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name FormList
        */

        filter_function: null,

        /**
        * initializes the view with optional parameters
        * @memberof FormList.prototype
        * @param {object} options
        * @param {boolean} options.graphModel - a reference to the selected {@link GraphModel}
        */
        initialize: function(options) {
            this.items = options.forms
            ListView.prototype.initialize.apply(this, arguments);
        },

        /**
        * Selects the passed in node
        * @memberof FormList.prototype
        * @param {object} item - the node to be selected via {@link GraphModel#selectNode}
        * @param {object} evt - click event object
        */
        selectItem: function(item, evt){
            this.trigger('select', item);
        },

    });
    return FormList;
});
