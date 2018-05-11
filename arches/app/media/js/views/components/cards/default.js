define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches'
], function ($, _, ko, koMapping, arches) {
    var viewModel = function(params) {
        var self = this;
        this._tileData = ko.observable(koMapping.toJSON(params.tile.data));
        this.loading = params.loading || ko.observable(false);
        this.card = params.card;
        this.tile = params.tile;
        this.form = params.form;
        this.expanded = ko.observable(true);
        this.dirty = ko.computed(function () {
            if (this.card.widgets.length === 0) {
                return true;
            }
            return this._tileData() !== koMapping.toJSON(this.tile.data);
        }, this);
        this.dirty.subscribe(function (dirty) {
            this.card.dirty(dirty);
        }, this)
        this.cancel = function () {
            ko.mapping.fromJS(
                JSON.parse(self._tileData()),
                self.tile.data
            );
        };
        var getTileData = function (tile) {
            var childTiles = {};
            if (tile.cards) {
                childTiles = _.reduce(tile.cards, function (tiles, card) {
                    return tiles.concat(card.tiles());
                }, []).reduce(function (tileLookup, childTile) {
                    tileLookup[childTile.tileid] = getTileData(childTile)
                    return tileLookup;
                }, {});
            }
            var tileData = {};
            if (tile.data) {
                tileData = koMapping.toJS(tile.data);
            }
            return {
                "tileid": tile.tileid,
                "data": tileData,
                "nodegroup_id": tile.nodegroup_id,
                "parenttile_id": tile.parenttile_id,
                "resourceinstance_id": tile.resourceinstance_id,
                "tiles": childTiles
            }
        };
        this.save = function () {
            self.loading(true);
            delete self.tile.formData.data;
            self.tile.formData.append(
                'data',
                JSON.stringify(
                    getTileData(self.tile)
                )
            );

            $.ajax({
                    type: "POST",
                    url: arches.urls.tile,
                    processData: false,
                    contentType: false,
                    data: self.tile.formData
                }).done(function(response) {
                    if (typeof self.tile.update === 'function') {
                        self.tile.update(response);
                    }
                    self._tileData(koMapping.toJSON(self.tile.data));
                }).fail(function(response) {
                    console.log('there was an error ', response);
                }).always(function(){
                    self.loading(false);
                })
        }
        this.deleteTile = function () {
            self.loading(true);
            $.ajax({
                    type: "DELETE",
                    url: arches.urls.tile,
                    data: JSON.stringify(getTileData(self.tile))
                }).done(function(response) {
                    self.tile.deleteTile();
                }).fail(function(response) {
                    console.log('there was an error ', response);
                }).always(function(){
                    self.loading(false);
                })
        }
    };
    return ko.components.register('default-card', {
        viewModel: viewModel,
        template: { require: 'text!templates/views/components/cards/default.htm' }
    });
});
