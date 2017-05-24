define([
    'backbone',
    'knockout',
    'models/card',
    'bindings/sortable'
], function(Backbone, ko, CardModel) {
    var CardComponentsTree = Backbone.View.extend({
        /**
        * A backbone view representing a card components tree
        * @augments Backbone.View
        * @constructor
        * @name CardComponentsTree
        */

        /**
        * Initializes the view with optional parameters
        * @memberof CardComponentsTree.prototype
        */
        initialize: function(options) {
            this.cards = ko.observableArray();
            options.cards.forEach(function(card){
                this.cards.push(new CardModel({
                    data: card,
                    datatypes: options.datatypes
                }));
            }, this);
            this.selection = ko.observable(this.cards()[0]);
        },

        /**
        * beforeMove - prevents dropping of tree nodes into other lists
        * this provides for sorting within cards and card containers, but
        * prevents moving of cards/widgets between containers/cards
        * @memberof CardComponentsTree.prototype
        * @param  {object} e - the ko.sortable event object
        */
        beforeMove: function (e) {
            e.cancelDrop = (e.sourceParent!==e.targetParent);
        }
    });
    return CardComponentsTree;
});
