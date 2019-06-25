define([
    'knockout',
    'viewmodels/card-component',
    'chosen'
], function(ko, CardComponentViewModel) {
    
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


            this.saveTiles = function(){
                console.log('in saveTiles');
                var self = this;
                var errors = [];
                var tile = this.groupedTiles().pop();
                tile.save(function(response) {
                    errors.push(response);
                        //params.form.alert(new AlertViewModel('ep-alert-red', response.responseJSON.message[0], response.responseJSON.message[1], null, function(){}));
                }, function(response){
                    var resourceInstanceId = response.resourceinstance_id;
                    _.each(self.groupedTiles(), function(tile) {
                        tile.resourceinstance_id = resourceInstanceId;
                        tile.save(function(response) {
                            errors.push(response);
                            //params.form.alert(new AlertViewModel('ep-alert-red', response.responseJSON.message[0], response.responseJSON.message[1], null, function(){}));
                        });
                    }, self);
                });
                //errors.forEach
            };

            this.deleteTiles = function(){
                console.log('in deleteTiles');
            };

            this.resetTiles = function(){
                console.log('in resetTiles');
            };

            this.selectGroupCard = function(blah) {
                console.log('selectGroupCard');
                console.log(blah)
                populateCardTiles();
                this.card.selected(true);
            };

        },
        template: {
            require: 'text!templates/views/components/cards/grouping.htm'
        }
    });
});
