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
                    edit.tileid = self.selectedProvisionalTile().tileid();
                    self.edits.push(koMapping.fromJS(edit))
            });
        }

        self.deleteProvisionalEdit = function(val){
            $.ajax({
                url: arches.urls.delete_provisional_tile,
                context: this,
                method: 'POST',
                dataType: 'json',
                data: koMapping.toJS(val)
            })
            .done(function(data) {
                self.edits.remove(val);
                self.form.loadForm(self.form.formid);
            })
            .fail(function(data) {
                console.log('Related resource request failed', data)
            });
        }

        self.acceptProvisionalEdit = function(val){
            this.selectedProvisionalTile().data = val.value
            var tile = this.selectedProvisionalTile()
            this.form.saveTile(this.parentTile, this.cardinality, this.selectedProvisionalTile())
            this.form.on('after-update', function(){
                this.deleteProvisionalEdit(val);
            }, this)
        }

        self.rejectProvisionalEdit = function(val){
            self.deleteProvisionalEdit(val);
        }

        self.findCard = function(cards, nodegroupid){
            _.each(cards, function(card) {
                if (card.get('nodegroup_id') == nodegroupid) {
                    this.card = card
                }
                if (this.card == null) {
                    self.findCard(card.get('cards')(), nodegroupid)
                }
            }, self);
        }

        self.selectedProvisionalTile = params.selectedProvisionalTile
        self.selectedProvisionalTile.subscribe(function(val) {
            self.edits.removeAll();
            if (val) {
                self.findCard(this.cards(), val.nodegroup_id())
                this.parseProvisionalEdits(val.provisionaledits());
            }
        }, self)
    };

    return ProvisionalTileViewModel;
});
