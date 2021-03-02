define([
    'jquery',
    'knockout',
    'arches',
    'views/components/workflows/new-tile-step',
    'views/components/workflows/component-based-step',
    'viewmodels/alert'
], function($, ko, arches, NewTileStepViewModel, ComponentBasedStepViewModel, AlertViewModel) {

    /** 
     * A generic viewmodel for workflow steps that can add multiple tiles
     * @name MultipleTileStepViewModel
     **/

    function MultipleTileStepViewModel(params) {
        var self = this;

        console.log("MultipleTileStepViewModel", self, params)



        ComponentBasedStepViewModel.apply(this, [params]);
        // NewTileStepViewModel.apply(this, [params]);

        this.itemName = ko.observable();
        if (ko.unwrap(params.title)) {
            this.itemName(ko.unwrap(params.title));
        }
        else {
            this.itemName('Items');
        }






        this.initialize = function() {
            console.log("MultipleTileStepViewModel initialize", self, params)

            // var url = arches.urls.api_card + this.getCardResourceIdOrGraphId();

            // $.getJSON(url, function(data) {
            //     console.log('MultipleTileStepViewModel API CALL RESULT', self, params, data)
            // });

            // super.initialize();

        };




        this.getCardResourceIdOrGraphId = function() { // override for different cases
            return (ko.unwrap(this.resourceId) || ko.unwrap(params.graphid));
        };








        this.addTileData = function(data, parent) {
            console.log(data, parent);
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

        // this.onSaveSuccess = function(tile) {
        //     params.resourceid(tile.resourceinstance_id);
        //     params.tileid(tile.tileid);
        //     self.resourceId(tile.resourceinstance_id);
        //     self.tile(self.card().getNewTile());
        //     self.tile().reset();
        //     setTimeout(function() {
        //         self.tile().reset();
        //     }, 1);
        // };

        // var updateTileOnInit = self.tile.subscribe(function() {
        //     updateTileOnInit.dispose();
        //     self.tile(self.card().getNewTile());
        // });

        this.initialize();
    }
    ko.components.register('multiple-tile-step', {
        viewModel: MultipleTileStepViewModel,
        template: {
            require: 'text!templates/views/components/workflows/multiple-tile-step.htm'
        }
    });
    return MultipleTileStepViewModel;
});
