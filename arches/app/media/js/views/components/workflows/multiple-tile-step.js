define([
    'knockout',
    'views/components/workflows/new-tile-step',
    'viewmodels/alert'
], function(ko, NewTileStepViewModel, AlertViewModel) {

    /** 
     * A generic viewmodel for workflow steps that can add multiple tiles
     * @name MultipleTileStepViewModel
     **/

    function MultipleTileStepViewModel(params) {
        var self = this;

        NewTileStepViewModel.apply(this, [params]);

        this.itemName = ko.observable();

        if (ko.unwrap(params.title)) {
            this.itemName(ko.unwrap(params.title));
        }
        else {
            this.itemName('Items');
        }


        this.add = function(foo) {
            console.log(foo);
        };




        this.remove = function(tile) {
            tile.deleteTile( function(response) {
                self.alert(new AlertViewModel(
                    'ep-alert-red', 
                    response.responseJSON.title,
                    response.responseJSON.message,
                    null, 
                    function(){ return; }
                ));
            });
        };

        this.edit = function(tile) { self.tile(tile); };

        this.onSaveSuccess = function(tile) {
            params.resourceid(tile.resourceinstance_id);
            params.tileid(tile.tileid);
            self.resourceId(tile.resourceinstance_id);
            self.tile(self.card().getNewTile());
            self.tile().reset();
            setTimeout(function() {
                self.tile().reset();
            }, 1);
        };

        var updateTileOnInit = self.tile.subscribe(function() {
            updateTileOnInit.dispose();
            self.tile(self.card().getNewTile());
        });
    }
    ko.components.register('multiple-tile-step', {
        viewModel: MultipleTileStepViewModel,
        template: {
            require: 'text!templates/views/components/workflows/multiple-tile-step.htm'
        }
    });
    return MultipleTileStepViewModel;
});
