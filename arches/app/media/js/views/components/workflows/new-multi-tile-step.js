define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'models/graph',
    'viewmodels/card',
    'viewmodels/tile',
    'views/components/workflows/new-tile-step',
    'viewmodels/provisional-tile',
    'viewmodels/alert'
], function(_, $, arches, ko, GraphModel, CardViewModel, TileViewModel, NewTileStepViewModel, ProvisionalTileViewModel, AlertViewModel) {

    /** 
     * A generic viewmodel for workflow steps that can add multiple tiles
     * @name NewMultiTileStepViewModel
     **/

    function NewMultiTileStepViewModel(params) {
        NewTileStepViewModel.apply(this, [params]);
        var self = this;

        this.remove = function(tile) {
            self.card().tiles.remove(tile);
        };

        this.edit = function(tile) {
            console.log(self.tile()._tileData());
            self.tile(tile);
        }

        self.saveTile = function(tile, callback) {
            self.loading(true);
            tile.save(function(response) {
                console.log("failed");
                self.loading(false);
                self.alert(
                    new AlertViewModel(
                        'ep-alert-red',
                        response.responseJSON.message[0],
                        response.responseJSON.message[1],
                        null,
                        function(){ return; }
                    )
                );
            }, function(tile) {
                console.log(tile);
                var newTile = new TileViewModel({
                    tile: tile,
                    card: self.card,
                    graphModel: params.graphModel,
                    resourceId: self.resourceId,
                    displayname: self.displayname,
                    handlers: self.handlers,
                    userisreviewer: params.userisreviewer,
                    cards: self.tile.cards,
                    tiles: [],
                    provisionalTileViewModel: params.provisionalTileViewModel,
                    scrollTo: ko.observable(),
                    loading: ko.observable(),
                    filter: ko.observable(),
                    cardwidgets: params.cardwidgets,
                });
                params.resourceid(tile.resourceinstance_id);
                params.tileid(tile.tileid);
                self.resourceId(tile.resourceinstance_id);
                self.complete(true);
                if (typeof callback === 'function') {
                    callback.apply(null, arguments);
                }
                self.tile(self.card().getNewTile());
                self.tile().reset();
                self.loading(false);
            });
        };
    }
    ko.components.register('new-multi-tile-step', {
        viewModel: NewMultiTileStepViewModel,
        template: {
            require: 'text!templates/views/components/workflows/new-multi-tile-step.htm'
        }
    });
    return NewMultiTileStepViewModel;
});
