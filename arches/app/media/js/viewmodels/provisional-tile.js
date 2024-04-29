define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'moment',
    'arches',
    'utils/set-csrf-token',
    'views/components/simple-switch',
], function($, _, ko, koMapping, moment, arches) {
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
        self.edits = ko.observableArray();
        self.users = [];
        self.selectedTile = params.tile;
        self.provisionaledits = ko.observableArray();
        self.declineUnacceptedEdits = ko.observable(true);
        self.selectedProvisionalEdit = ko.observable();

        // function csrfSafeMethod(method) {
        //     // these HTTP methods do not require CSRF protection
        //     return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        // }
        // $.ajaxSetup({
        //     beforeSend: function(xhr, settings) {
        //         console.log("DSIDS()DS()")
        //         if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        //             xhr.setRequestHeader("X-CSRFToken", Cookies.get('csrftoken'));
        //         }
        //     }
        // });
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
                    });
                })
                .fail(function() {
                    // console.log('User name request failed', data)
                });
        };

        self.updateProvisionalEdits = function(tile) {
            var isfullyprovisional;
            if (tile && tile.data) {
                var users = [];
                var data = koMapping.toJS(tile.data);
                var provisionaleditlist = _.map(ko.unwrap(tile.provisionaledits), function(edit, key){
                    users.push(key);
                    edit['username'] = ko.observable('');
                    edit['displaytimestamp'] = moment(edit.timestamp).format("hh:mm");
                    edit['displaydate'] = moment(edit.timestamp).format("DD-MM-YYYY");
                    edit['user'] = key;
                    if (edit.isfullyprovisional === undefined) {
                        edit['isfullyprovisional'] = ko.observable(false);
                    }
                    return edit;
                }, this);
                this.provisionaledits(_.sortBy(provisionaleditlist, function(pe){return moment(pe.timestamp);}));
                if (this.provisionaledits().length > 0) {
                    if (ko.unwrap(this.provisionaledits()[0].isfullyprovisional) === true) {
                        isfullyprovisional = true;
                    }
                }
                if ((data && _.keys(data).length === 0 && ko.unwrap(tile.provisionaledits)) ||  isfullyprovisional) {
                    self.selectedProvisionalEdit(undefined);
                    if (this.provisionaledits().length > 0) {
                        this.provisionaledits()[0].isfullyprovisional(true);
                        koMapping.fromJS(this.provisionaledits()[0]['value'], tile.data);
                        this.selectedProvisionalEdit(this.provisionaledits()[0]);
                        tile._tileData.valueHasMutated();
                    }
                } else if (self.selectedProvisionalEdit()) {
                    self.selectedProvisionalEdit(undefined);
                    self.selectedTile().reset();
                }
                this.getUserNames(this.provisionaleditlist, users);
            }
        };

        self.removeSelectedProvisionalEdit = function() {
            this.provisionaledits.remove(this.selectedProvisionalEdit());
            this.selectedProvisionalEdit(undefined);
        };

        self.selectProvisionalEdit = function(val){
            if (self.selectedProvisionalEdit() != val) {
                self.selectedProvisionalEdit(val);
                koMapping.fromJS(val['value'], self.selectedTile().data);
                self.selectedTile().parent.params.handlers['tile-reset'].forEach(handler => handler(self.selectedTile()));
                self.selectedTile().parent.widgets().forEach(
                    function(w){
                        var defaultconfig = w.widgetLookup[w.widget_id()].defaultconfig;
                        if (defaultconfig.rerender === true && self.selectedTile().parent.allowProvisionalEditRerender() === true) {
                            w.label.valueHasMutated();
                        } 
                    });
                if (self.selectedTile().parent.triggerUpdate) {
                    self.selectedTile().parent.triggerUpdate();
                }
            }
        };

        self.resetAuthoritative = function(){
            self.selectedProvisionalEdit(undefined);
            self.selectedTile().reset();
        };

        self.tileIsFullyProvisional = ko.computed(function() {
            return self.selectedProvisionalEdit() && ko.unwrap(self.selectedProvisionalEdit().isfullyprovisional) === true;
        });

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
                    if (data.result === 'delete') {
                        this.selectedTile().deleteTile();
                    } else {
                        var user = val.user;
                        var provisionaledits = this.selectedTile().provisionaledits();
                        delete provisionaledits[user];
                        this.selectedTile().provisionaledits(provisionaledits);
                        if (self.selectedProvisionalEdit() === val) {
                            self.selectedProvisionalEdit(undefined);
                            self.selectedTile().reset();
                        }
                        self.provisionaledits.remove(val);
                        if (_.keys(this.selectedTile().provisionaledits()).length === 0) {
                            this.selectedTile().provisionaledits(null);
                        }
                    }
                    self.selectedTile()._tileData.valueHasMutated();
                })
                .fail(function(data) {
                    console.log('request failed', data);
                });
        };

        self.deleteAllProvisionalEdits = function() {
            var users = _.map(self.provisionaledits(), function(edit){return edit.user;});
            $.ajax({
                url: arches.urls.delete_provisional_tile,
                context: this,
                method: 'POST',
                dataType: 'json',
                data: {'users': JSON.stringify(users), 'tileid': this.selectedTile().tileid }
            })
                .done(function(data) {
                    if (data.result === 'delete') {
                        this.selectedTile().deleteTile();
                    } else {
                        self.selectedTile().reset();
                        self.selectedProvisionalEdit(undefined);
                        self.provisionaledits.removeAll();
                        this.selectedTile().provisionaledits(null);
                    }
                })
                .fail(function(data) {
                    console.log('request failed', data);
                });
        };


        self.acceptProvisionalEdit = function(){
            var provisionaledits = this.selectedTile().provisionaledits();
            var user = this.selectedProvisionalEdit().user;
            if (provisionaledits) {
                delete provisionaledits[user];
                if (_.keys(this.selectedTile().provisionaledits()).length === 0) {
                    this.selectedTile().provisionaledits(null);
                }
                this.provisionaledits.remove(this.selectedProvisionalEdit());
                this.selectedProvisionalEdit(undefined);
            }
        };

        self.rejectProvisionalEdit = function(val){
            self.deleteProvisionalEdit(val);
        };

    };

    return ProvisionalTileViewModel;
});
