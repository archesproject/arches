define([
    'knockout'
], function(ko) {
    return ko.components.register('new-tile-step', {
        viewModel: function(params) {
            console.log(params);
            this.componentname = 'default';
            this.selectedCard = '';
            this.selectedTile = null;
            this.provisionalTileViewModel = null;
            this.reviewer = null;
            this.loading = ko.observable(false);
        },
        template: {
            require: 'text!templates/views/components/workflows/new-tile-step.htm'
        }
    });
});
