define([
    'knockout',
    'viewmodels/card-component',
    'chosen'
], function(ko, CardComponentViewModel) {
    var flattenTree = function(parents, flatList) {
        _.each(ko.unwrap(parents), function(parent) {
            flatList.push(parent);
            flattenTree(
                ko.unwrap(parent.cards),
                flatList
            );
        }, this);
        return flatList;
    };
    return ko.components.register('grouping-card-component', {
        viewModel: function(params) {
            // params.form is the CardTreeViewModel
            params.configKeys = ['groupedCards'];
            CardComponentViewModel.apply(this, [params]);
            //if (params.state !== 'editor-tree') {
                var cards = !!params.card.parent ? params.card.parent.cards : flattenTree(params.card.topCards, []);
                this.cardLookup = {};
                this.siblingCards = ko.observableArray();
                _.each(cards, function(card) {
                    this.cardLookup[card.model.id] = card;
                    if (card.parentCard === params.card.parentCard &&
                        card.cardinality === '1' &&
                        card !== params.card &&
                        card.cards().length === 0) {
                        this.siblingCards.push({'name': card.model.name(), 'id': card.model.id});
                    }
                }, this);

                // this.groupedCards = ko.observableArray();
                // params.card.model.set('config', this.groupedCards);

                // this.siblingCards = ko.observableArray([
                //     {'name': 'card1', 'id': 'alskdj'}, {'name': 'card2', 'id': 'alskdsdj'}, {'name': 'card3', 'id': 'da'}]);


            //}
        },
        template: {
            require: 'text!templates/views/components/cards/grouping.htm'
        }
    });
});
