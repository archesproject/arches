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
            var self = this;
            // params.form is the CardTreeViewModel
            var populateCardTiles = function() {
                _.each(self.groupedCards().concat(self.card.model.id), function(cardid) {
                    var card = self.cardLookup[cardid];
                    if (card.tiles().length === 0) {
                        card.tiles.push(card.getNewTile());
                    }
                }, self);
            };
            params.configKeys = ['groupedCards'];
            
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

            if (!!params.preview) {
                populateCardTiles();
            }

            this.groupedTiles = ko.computed(function() {
                var tiles = [];
                _.each(this.groupedCards().concat(this.card.model.id), function(cardid) {
                    var card = this.cardLookup[cardid];
                    if (card.tiles().length > 0) {
                        tiles.push(card.tiles()[0]);
                    }
                }, this);
                return tiles;
            }, this);


            this.dirty = ko.computed(function() {
                return _.find(this.groupedTiles(), function(tile) {
                    return tile.dirty();
                }, this);
            }, this);


            this.previouslySaved = ko.computed(function() {
                return _.find(this.groupedTiles(), function(tile) {
                    return !!tile.tileid;
                }, this);
            }, this);


            this.saveTiles = function(){
                var self = this;
                var errors = ko.observableArray().extend({ rateLimit: 250 });
                var tile = this.groupedTiles()[0];
                tile.save(function(response) {
                    errors.push(response);
                }, function(response){
                    var resourceInstanceId = response.resourceinstance_id;
                    _.each(_.rest(self.groupedTiles()), function(tile) {
                        tile.resourceinstance_id = resourceInstanceId;
                        tile.save(function(response) {
                            errors.push(response);
                        });
                    }, self);
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
                console.log('in deleteTiles');
                params.loading(true);
                var self = this;
                var errors = ko.observableArray().extend({ rateLimit: 250 });
                var tilesToRemove = [];
                
                var requests = self.groupedTiles().map(function(tile) {
                    return $.ajax({
                        type: "DELETE",
                        url: arches.urls.tile,
                        data: JSON.stringify(tile.getData())
                    }).done(function(response) {
                        //tile.parent.tiles.remove(tile);
                        tilesToRemove.push(tile);
                        //selection(params.card);
                    }).fail(function(response) {
                        errors.push(response);
                    });
                }, self);

                Promise.all(requests).then(function(ret) {
                }).finally(function(){
                    params.loading(false);
                    tilesToRemove.forEach(function(tileToRemove){
                        var card = tileToRemove.parent;
                        card.tiles.replace(tileToRemove, card.getNewTile());
                        card.tiles.valueHasMutated();
                    });
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
                console.log('in resetTiles');
            };

            this.selectGroupCard = function() {
                populateCardTiles();
                this.card.selected(true);
            };

        },
        template: {
            require: 'text!templates/views/components/cards/grouping.htm'
        }
    });
});
