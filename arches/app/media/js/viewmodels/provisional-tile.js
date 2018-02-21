define(['knockout', 'knockout-mapping', 'arches'], function (ko, koMapping, arches) {
    /**
    * A viewmodel for managing provisional edits
    *
    * @constructor
    * @name ProvisionalTileViewModel
    *
    * @param  {string} params - a configuration object
    */
    var ProvisionalTileViewModel = function(params) {
        var self = this;
        self.card = null;
        self.edits = ko.observableArray()
        self.parseProvisionalEdits = function(editsjson){
            _.each(JSON.parse(editsjson), function(edit, key){
                    edit.user = key;
                    self.edits.push(koMapping.fromJS(edit))
            });
        }

        self.selectedProvisionalTile = params.selectedProvisionalTile
        self.selectedProvisionalTile.subscribe(function(val) {
            _.each(this.cards(), function(card) {
                if (card.get('nodegroup_id') == val.nodegroup_id()) {
                    this.card = card
                }
            }, self);
            this.parseProvisionalEdits(val.provisionaledits());
        }, self)
    };

    return ProvisionalTileViewModel;
});
