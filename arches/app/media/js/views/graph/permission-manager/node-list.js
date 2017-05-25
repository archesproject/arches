define([
    'backbone',
    'knockout',
    'models/card',
    'views/list',
    'bindings/sortable'
], function(Backbone, ko, CardModel, ListView) {
    var GroupedNodeList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name GroupedNodeList
        */

        single_select: false,

        /**
        * initializes the view with optional parameters
        * @memberof GroupedNodeList.prototype
        * @param {object} options
        * @param {boolean} options.permissions - a list of allowable permissions
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            //this.items = options.items;

            //this.items = ko.observableArray();
            this.outerCards = options.cards.children;

            var parseData = function(item){
                if ('nodegroup' in item){
                    this.items.push(item);
                }else{
                    item.selectable = false;
                }
                item.children.forEach(parseData, this);
            }

            parseData.call(this, options.cards);

            this.datatypes = {};
            options.datatypes.forEach(function(datatype){
                this.datatypes[datatype.datatype] = datatype.iconclass;
            }, this);

            //this.selection = ko.observable(this.items()[0]);
            ListView.prototype.initialize.apply(this, arguments);
        }

    });
    return GroupedNodeList;
});
