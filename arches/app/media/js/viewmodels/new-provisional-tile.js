define([
    'knockout',
    'knockout-mapping',
    'moment',
    'arches',
    'views/components/simple-switch'
], function (ko, koMapping, moment, arches) {
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
        self.users = []
        self.selectedTile = params.tile;
        self.provisionaledits = ko.observableArray();
        self.declineUnacceptedEdits = ko.observable(true);
        self.selectedProvisionalTile = ko.observable();

        self.getUserNames = function(edits, users){
            $.ajax({
                url: arches.urls.get_user_names,
                context: this,
                method: 'POST',
                data: { userids: JSON.stringify(users) },
                dataType: 'json'
            })
            .done(function(data) {
                _.each(this.provisionaledits(), function(edit) {
                    edit.username(data[edit.user]);
                })
            })
            .fail(function(data) {
                console.log('User name request failed', data)
            });
        }

        self.updateProvisionalEdits = function(tile) {
            if (tile.data) {
                var users = [];
                var data = koMapping.toJS(tile.data);
                var provisionaleditlist = _.map(tile.provisionaledits(), function(edit, key){
                    users.push(key);
                    edit['username'] = ko.observable('');
                    edit['user'] = key;
                    return edit;
                }, this);
                this.provisionaledits(_.sortBy(provisionaleditlist, function(pe){return moment(pe.timestamp)}));
                if (data && _.keys(data).length === 0 && tile.provisionaledits()) {
                    koMapping.fromJS(this.provisionaledits()[0]['value'], tile.data);
                    tile._tileData.valueHasMutated()
                };
                this.getUserNames(this.provisionaleditlist, users);
            };
        };

        self.updateProvisionalEdits(self.selectedTile);

        self.selectedTile.subscribe(self.updateProvisionalEdits, this);



        // self.deleteProvisionalEdit = function(val){
        //     $.ajax({
        //         url: arches.urls.delete_provisional_tile,
        //         context: this,
        //         method: 'POST',
        //         dataType: 'json',
        //         data: koMapping.toJS(val)
        //     })
        //     .done(function(data) {
        //         self.edits.remove(val);
        //         self.form.loadForm(self.selectedForm());
        //     })
        //     .fail(function(data) {
        //         console.log('Related resource request failed', data)
        //     });
        // }

        // self.deleteAllProvisionalEdits = function() {
        //     var edits = koMapping.toJSON({'edits':self.edits()})
        //     $.ajax({
        //         url: arches.urls.delete_provisional_tile,
        //         context: this,
        //         method: 'POST',
        //         dataType: 'json',
        //         data: {payload: edits}
        //     })
        //     .done(function(data) {
        //         self.edits.removeAll();
        //         self.form.loadForm(self.selectedForm());
        //     })
        //     .fail(function(data) {
        //         console.log('Related resource request failed', data)
        //     });
        // }

        // self.acceptProvisionalEdit = function(val){
        //     self.loading(true);
        //     this.selectedProvisionalTile().data = val.value
        //     var tile = this.selectedProvisionalTile()
        //     this.form.saveTile(this.parentTile, this.cardinality, this.selectedProvisionalTile())
        //     this.form.on('after-update', function(){
        //         if (this.declineUnacceptedEdits()) {
        //             this.deleteAllProvisionalEdits();
        //         } else {
        //             this.deleteProvisionalEdit(val);
        //         }
        //         this.loading(false);
        //     }, this)
        // }
        //
        // self.rejectProvisionalEdit = function(val){
        //     self.deleteProvisionalEdit(val);
        // }
        //
        // self.findCard = function(cards, nodegroupid){
        //     _.each(cards, function(card) {
        //         if (card.get('nodegroup_id') == nodegroupid) {
        //             this.card = card
        //         }
        //         if (this.card == null) {
        //             self.findCard(card.get('cards')(), nodegroupid)
        //         }
        //     }, self);
        // }
        //
        // self.selectedProvisionalTile = params.selectedProvisionalTile
        // self.selectedProvisionalTile.subscribe(function(val) {
        //     if (!self.selectedForm()) {
        //         self.selectedForm(self.form.formid)
        //     };
        //     self.edits.removeAll();
        //     if (val) {
        //         self.card = null;
        //         self.findCard(this.cards(), val.nodegroup_id())
        //         this.parseProvisionalEdits(val.provisionaledits());
        //         this.getUserNames(self.edits())
        //     }
        // }, self)
    };

    return ProvisionalTileViewModel;
});
