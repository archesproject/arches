import Backbone from "backbone";
import _ from "underscore";
import ko from "knockout";
import widgets from "widgets";
import "bindings/sortable";


var CardFormPreview = Backbone.View.extend({
    /**
    * A backbone view representing a card form preview
    * @augments Backbone.View
    * @constructor
    * @name CardFormPreview
    */

    /**
    * Initializes the view with optional parameters
    * @memberof CardFormPreview.prototype
    */
    initialize: function(options) {
        var self = this;
        this.card = options.card;
        this.graph = options.graphModel;
        this.selection = options.selection || ko.observable(this.card);
        this.helpPreviewActive = options.helpPreviewActive || ko.observable(false);
        this.widgetLookup = widgets;
        this.currentTabIndex = ko.computed(function() {
            if (!self.card.isContainer() || self.selection() === self.card) {
                return 0;
            }
            var card = self.selection();
            if (card.node) {
                card = card.card;
            }
            var index = self.card.get('cards')().indexOf(card);
            return index;
        });
        this.currentTabCard = ko.computed(function() {
            if(this.card.get('cards')().length === 0){
                return this.card;
            }else{
                return this.card.get('cards')()[this.currentTabIndex()];
            }
        }, this);
    },

    /**
    * beforeMove - prevents dropping of widgets/tabs into other cards
    * this provides for sorting within preview and tabs, but prevents
    * moving of cards/widgets between containers/cards
    * @memberof CardFormPreview.prototype
    * @param  {object} e - the ko.sortable event object
    */
    beforeMove: function(e) {
        e.cancelDrop = (e.sourceParent!==e.targetParent);
    }
});
export default CardFormPreview;

