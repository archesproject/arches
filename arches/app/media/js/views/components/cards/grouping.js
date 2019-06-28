define([
    'knockout',
    'arches',
    'viewmodels/card-component',
    'viewmodels/alert',
    'chosen'
], function(ko, arches, CardComponentViewModel, AlertViewModel) {
    
    var flattenTree = function(parents, flatList) {
        _.each(ko.unwrap(parents), function(parent) {
            flatList.push(parent);
            flattenTree(
                ko.unwrap(parent.cards),
                flatList
            );
        }, this);
        return flatList;
    };
    
    return ko.components.register('grouping-card-component', {
        viewModel: function(params) {
            // params.form is the CardTreeViewModel
            var self = this;
            this.saving = false;
            this.tiles = [];

            params.configKeys = ['groupedCardIds'];
            CardComponentViewModel.apply(this, [params]);

            var cards = !!params.card.parent ? params.card.parent.cards : flattenTree(params.card.topCards, []);
            this.cardLookup = {};
            this.siblingCards = ko.observableArray();
            
            _.each(cards, function(card) {
                this.cardLookup[card.model.id] = card;
                if (card.parentCard === params.card.parentCard &&
                    card.cardinality === '1' &&
                    card !== params.card &&
                    card.cards().length === 0) {
                    this.siblingCards.push({'name': card.model.name(), 'id': card.model.id});
                }
            }, this);

            this.groupedCards = ko.computed(function(){
                return _.map([this.card.model.id].concat(this.groupedCardIds()), function(cardid) {
                    return self.cardLookup[cardid];
                }, this);
            }, this);

            if (!!params.preview) {
                _.each(this.groupedCards(), function(card) {
                    if (card.tiles().length === 0) {
                        card.tiles.push(card.getNewTile());
                    }
                    _.each(card.widgets(), function(widget) {
                        widget.parent = self.card;
                    })
                }, this);
            }

            this.groupedTiles = ko.computed(function() {
                if (this.saving) {
                    return this.tiles;
                } else {
                    var tiles = [];
                    _.each(this.groupedCards(), function(card) {
                        if (card.tiles().length > 0) {
                            tiles.push(card.tiles()[0]);
                        } else {
                            tiles.push(card.getNewTile());
                        }
                    }, this);
                    this.tiles = tiles;
                    return tiles;
                }
            }, this);

            this.getTile = function(cardid) {
                var tile = _.find(this.groupedTiles(), function(tile) {
                    return tile.parent.model.id === cardid;
                });
                if (!tile && !!params.preview) {
                    tile = self.cardLookup[cardid].getNewTile();
                }
                return tile;
            };

            this.dirty = ko.computed(function() {
                return _.find(this.groupedTiles(), function(tile) {
                    return tile.dirty();
                }, this);
            }, this);

            this.previouslySaved = ko.computed(function() {
                return !!(_.find(this.groupedTiles(), function(tile) {
                    return !!tile.tileid;
                }, this));
            }, this);

            this.saveTiles = function(){
                var self = this;
                var errors = ko.observableArray().extend({ rateLimit: 250 });
                var tiles = this.groupedTiles();
                var tile = this.groupedTiles()[0];
                this.saving = true;
                var requests = [];
                tile.save(function(response) {
                    errors.push(response);
                    self.saving = false;
                    self.groupedCardIds.valueHasMutated();
                    self.selectGroupCard();
                }, function(response){
                    var resourceInstanceId = response.resourceinstance_id;
                    var requests = _.map(_.rest(tiles), function(tile) {
                        tile.resourceinstance_id = resourceInstanceId;
                        return tile.save(function(response) {
                            errors.push(response);
                        });
                    }, self);
                    Promise.all(requests).finally(function(){
                        self.saving = false;
                        self.groupedCardIds.valueHasMutated();
                        self.selectGroupCard();
                    });
                });
                errors.subscribe(function(errors){
                    var title = [];
                    var message = [];
                    errors.forEach(function(response) {
                        title.push(response.responseJSON.message[0]);
                        message.push(response.responseJSON.message[1]);
                    });
                    params.form.alert(new AlertViewModel('ep-alert-red', title.join(), message.join(), null, function(){}));
                });
            };

            this.deleteTiles = function(){
                params.loading(true);
                var self = this;
                var errors = ko.observableArray().extend({ rateLimit: 250 });
                
                var requests = self.groupedTiles().map(function(tile) {
                    if (!!tile.tileid) {
                        return $.ajax({
                            type: "DELETE",
                            url: arches.urls.tile,
                            data: JSON.stringify(tile.getData())
                        }).done(function(response) {
                            tile.parent.tiles.remove(tile);
                        }).fail(function(response) {
                            errors.push(response);
                        });
                    }
                }, self);

                Promise.all(requests).finally(function(){
                    params.loading(false);
                    self.selectGroupCard();
                });
                errors.subscribe(function(errors){
                    var title = [];
                    var message = [];
                    errors.forEach(function(response) {
                        title.push(response.responseJSON.message[0]);
                        message.push(response.responseJSON.message[1]);
                    });
                    params.form.alert(new AlertViewModel('ep-alert-red', title.join(), message.join(), null, function(){}));
                });

            };

            this.resetTiles = function(){
                _.each(this.groupedTiles(), function(tile) {
                    tile.reset();
                }, this);
            };

            this.selectGroupCard = function() {
                this.card.selected(true);
            };

        },
        template: {
            require: 'text!templates/views/components/cards/grouping.htm'
        }
    });
});
