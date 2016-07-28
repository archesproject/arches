define([
    'backbone',
    'knockout',
    'bindings/sortable'
], function(Backbone, ko) {
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
            _.extend(this, _.pick(options, 'card'));
            this.selection = ko.observable(this.card);
        },

        beforeMove: function (e) {
            e.cancelDrop = (e.sourceParent!==e.targetParent);
        }
    });
    return CardComponentsTree;
});
