define([
    'backbone',
    'knockout',
    'views/list'
], function(Backbone, ko, ListView) {
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
        * @param {boolean} options.cards - a list of all cards (simplified json) for a resource model
        * @param {boolean} options.datatypes - a list of all datatypes
        */
        initialize: function(options) {

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

            this.showNodes = ko.observable(false);

            //this.selection = ko.observable(this.items()[0]);
            ListView.prototype.initialize.apply(this, arguments);
        }

    });
    return GroupedNodeList;
});
