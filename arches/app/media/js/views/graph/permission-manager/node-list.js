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

        single_select: true,

        /**
        * initializes the view with optional parameters
        * @memberof GroupedNodeList.prototype
        * @param {object} options
        * @param {boolean} options.permissions - a list of allowable permissions
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            //this.items = options.items;

            var filterableitems = ko.observableArray(options.cards.children);
            var outerCards = ko.observableArray();

            var parseCard = function(card){
                var item = {
                    'name': card.name,
                    'isContainer': !!card.cards.length,
                    'children': card.nodes
                };
                filterableitems.push(item);
                return item;
            }

            var parseCardContainer = function(card){
                var item = {
                    'name': card.name,
                    'isContainer': !!card.cards.length,
                    'children': []
                };
                filterableitems.push(item);
                if (!!card.cards.length) {
                    card.cards.forEach(function(card){
                        item.children.push(parseCard(card));
                    });
                }
                return item;
            }
            // options.cards.forEach(function(card){
            //     card.isOuter = true;
            //     if (!!card.cards.length) {
            //         outerCards.push(parseCardContainer(card));
            //     }else{
            //         outerCards.push(parseCard(card));
            //     }
            // }, this);

            this.items = filterableitems;
            this.outerCards = options.cards.children;
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
