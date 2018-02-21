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
            console.log('edit')
            _.each(JSON.parse(editsjson), function(edit, key){
                    edit.user = key;
                    edit.tileid = self.selectedProvisionalTile().tileid();
                    self.edits.push(koMapping.fromJS(edit))
            });
        }

        self.acceptProvisionalEdit = function(val){
            console.log(val)
        }

        self.rejectProvisionalEdit = function(val){
            $.ajax({
                    url: arches.urls.delete_provisional_tile,
                    context: this,
                    method: 'POST',
                    dataType: 'json',
                    data: koMapping.toJS(val)
                })
                .done(function(data) {
                    console.log('done', data)
                    self.edits.remove(val);
                    self.form.loadForm(self.form.formid);
                })
                .fail(function(data) {
                    console.log('Related resource request failed', data)
                });
        }

        self.selectedProvisionalTile = params.selectedProvisionalTile
        self.selectedProvisionalTile.subscribe(function(val) {
            self.edits.removeAll();
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
