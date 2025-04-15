import _ from 'underscore';
import ko from 'knockout';
import Backbone from 'backbone';
import 'bindings/sortable';


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
        this.selection = options.selection || ko.observable(this.card);
    },

    /**
    * beforeMove - prevents dropping of tree nodes into other lists
    * this provides for sorting within cards and card containers, but
    * prevents moving of cards/widgets between containers/cards
    * @memberof CardComponentsTree.prototype
    * @param  {object} e - the ko.sortable event object
    */
    beforeMove: function(e) {
        e.cancelDrop = (e.sourceParent!==e.targetParent);
    }
});
export default CardComponentsTree;
