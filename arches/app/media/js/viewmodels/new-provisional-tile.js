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
        self.selectedProvisionalEdit = ko.observable();

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
                    this.selectedProvisionalEdit(this.provisionaledits()[0])
                    tile._tileData.valueHasMutated()
                };
                this.getUserNames(this.provisionaleditlist, users);
            };
        };

        self.removeSelectedProvisionalEdit = function() {
            this.provisionaledits.remove(this.selectedProvisionalEdit());
            this.selectedProvisionalEdit(undefined);
        };

        self.selectProvisionalEdit = function(val){
            self.selectedProvisionalEdit(val);
            koMapping.fromJS(val['value'], self.selectedTile().data);
            self.selectedTile()._tileData.valueHasMutated()
        };

        self.updateProvisionalEdits(self.selectedTile);
        self.selectedTile.subscribe(self.updateProvisionalEdits, this);

        self.deleteProvisionalEdit = function(val){
            $.ajax({
                url: arches.urls.delete_provisional_tile,
                context: this,
                method: 'POST',
                dataType: 'json',
                data: {'user': koMapping.toJS(val).user, 'tileid': this.selectedTile().tileid }
            })
            .done(function(data) {
                if (self.selectedProvisionalEdit() === val) {
                    self.selectedProvisionalEdit(undefined);
                    self.selectedTile().reset();
                };
                self.provisionaledits.remove(val);
            })
            .fail(function(data) {
                console.log('request failed', data)
            });
        }

        self.deleteAllProvisionalEdits = function() {
            var users = _.map(self.provisionaledits(), function(edit){return edit.user});
            $.ajax({
                url: arches.urls.delete_provisional_tile,
                context: this,
                method: 'POST',
                dataType: 'json',
                data: {'users': JSON.stringify(users), 'tileid': this.selectedTile().tileid }
            })
            .done(function(data) {
                self.selectedTile().reset();
                self.selectedProvisionalEdit(undefined);
                self.provisionaledits.removeAll();
            })
            .fail(function(data) {
                console.log('request failed', data)
            });
        }


        self.acceptProvisionalEdit = function(){
            var provisionaledits = this.selectedTile().provisionaledits();
            var user = this.selectedProvisionalEdit().user
            if (provisionaledits) {
                delete provisionaledits[user]
                if (_.keys(this.selectedTile().provisionaledits()).length === 0) {
                    this.selectedTile().provisionaledits(null);
                }
                this.provisionaledits.remove(this.selectedProvisionalEdit());
                this.selectedProvisionalEdit(undefined);
            }
        };

        self.acceptEdit = function(val){
            this.selectProvisionalEdit(val);
            this.selectedTile().save();
        };

        self.rejectProvisionalEdit = function(val){
            console.log('rejecting')
            self.deleteProvisionalEdit(val);
        }

    };

    return ProvisionalTileViewModel;
});
