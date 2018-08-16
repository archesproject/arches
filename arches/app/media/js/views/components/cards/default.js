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
    };
    return ko.components.register('default-card', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/default.htm'
        }
    });
});
