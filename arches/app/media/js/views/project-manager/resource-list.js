define([
    'knockout',
    'arches',
    'views/list'
], function(ko, arches, ListView) {
    var ResourceList = ListView.extend({
        /**
        * A backbone view to manage a list of graph nodes
        * @augments ListView
        * @constructor
        * @name ResourceList
        */

        single_select: true,

        /**
        * initializes the view with optional parameters
        * @memberof ResourceList.prototype
        * @param {object} options
        * @param {boolean} options.permissions - a list of allowable permissions
        * @param {boolean} options.card - a reference to the selected {@link CardModel}
        */
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);
            var self = this;
            this.items = options.items;
            this.cardFilter = ko.observable('');

            this.initCards = function(cards){
                _.each(cards, function(card){
                    card.approved = ko.observable(false);
                    card.filtered = ko.observable(false);
                    card.approved.subscribe(function(val){
                        var item = item;
                    }, self)
                    card.expanded = ko.observable(false);
                    card.widgetlabels = _.map(card.widgets, function(w) {
                        return w.label
                    }).join(', ');
                    if (card.widgetlabels === "") {
                        card.widgetlabels = card.name;
                    };
                }, self)
            }

            _.each(this.items(), function(item){
                item.cards = item.cardsflat;
                self.initCards(item.cards())
                item.added = ko.computed(function(){
                    return _.filter(item.cards(), function(card){return card.approved()}).length > 0;
                })

                self.cardFilter.subscribe(function (val) {
                    if (item.selected()) {
                        _.each(item.cards(), function(card) {
                            if (val === '') {
                                card.filtered(false)
                            } else {
                                if (card.name.toLowerCase().indexOf(val.toLowerCase()) >= 0) {
                                    card.filtered(false);
                                } else {
                                    card.filtered(true);
                                };
                            };
                        });
                    }
                    });

                });

            this.resetCards = function(cards){
                _.each(this.items(), function(item){
                    item.cards.sort(function(a,b){
                        var inProjectCards = _.contains(cards, a.cardid) || _.contains(cards, b.cardid);
                        if (inProjectCards) {
                            res = cards.indexOf(a.cardid) < cards.indexOf(b.cardid) ? -1 : 1
                        } else {
                            res = a.name < b.name ? -1 : 1;
                        }
                        return res;
                    });
                    _.each(item.cards(), function(card){
                        if (_.contains(cards, card.cardid)) {
                            card.approved(true);
                        } else {
                            card.approved(false);
                        }
                    });
                })

            }

            this.selected = ko.computed(function(){
                var res = self.selectedItems().length > 0 ? self.selectedItems()[0] : '';
                return res;
            })
        }

    });
    return ResourceList;
});
