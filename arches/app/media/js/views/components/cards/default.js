define(['knockout', 'bindings/scrollTo'], function(ko) {
    var viewModel = function(params) {
        this.state = params.state || 'form';
        this.preview = params.preview;
        this.loading = params.loading || ko.observable(false);
        this.card = params.card;
        this.tile = params.tile;
        if (this.preview) {
            if (!this.card.newTile) {
                this.card.newTile = this.card.getNewTile();
            }
            this.tile = this.card.newTile;
        }
        this.form = params.form;
        this.provisionalTileViewModel = params.provisionalTileViewModel;
        this.reviewer = params.reviewer;
        this.expanded = ko.observable(true);
        this.beforeMove = function(e) {
            e.cancelDrop = (e.sourceParent!==e.targetParent);
        };
        this.selectChildCards = function(currentCard, value) {
            if (value !== undefined){
                currentCard.selected(value);
            } else {
                if (currentCard.selected() === false) {
                    value = true;
                    currentCard.selected(true);
                } else {
                    value = false;
                    currentCard.selected(false);
                }
            }
            currentCard.cards().forEach(function(childCard){
                this.selectChildCards(childCard, value);
            }, this);
        };
    };
    return ko.components.register('default-card', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/default.htm'
        }
    });
});
