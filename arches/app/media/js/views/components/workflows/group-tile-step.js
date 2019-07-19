define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'views/components/workflows/new-tile-step',
    'viewmodels/provisional-tile',
    'viewmodels/alert'
], function(_, $, arches, ko, koMapping, NewTileStep, ProvisionalTileViewModel, AlertViewModel) {
    function viewModel(params) {
        var self = this;
        NewTileStep.apply(this, [params]);
        self.onSaveSuccess = function(tiles) {
            self.tiles = tiles;
            tiles.forEach(function(tile){
                params.resourceid(tile.resourceinstance_id);
                self.resourceId(tile.resourceinstance_id);
            });
            if (self.completeOnSave === true) {
                self.complete(true);
            }
        };
    }
    ko.components.register('group-tile-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/new-tile-step.htm'
        }
    });
    return viewModel;
});
