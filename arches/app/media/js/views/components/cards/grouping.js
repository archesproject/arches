import _ from 'underscore';
import $ from 'jquery';
import ko from 'knockout';
import arches from 'arches';
import CardComponentViewModel from 'viewmodels/card-component';
import AlertViewModel from 'viewmodels/alert';
import groupingCardTemplate from 'templates/views/components/cards/grouping.htm';
import 'chosen';


var flattenTree = function(parents, flatList) {
    for (const parent of ko.unwrap(parents)) {
        flatList.push(parent);
        flattenTree(
            parent.cards,
            flatList
        );
    }
    return flatList;
};

function viewModel(params) {
    // params.form is the CardTreeViewModel
    var self = this;
        
    this.saving = params.form?.saving || ko.observable(false);
    this.tiles = [];
    this.widgetInstanceDataLookup = {};
    this.showGrid = params?.form?.showGrid;
    this.toggleGrid = params?.form?.toggleGrid;

    /*
        'sortedWidgetIds' originally referred to entries in the
        card_x_node_x_widget table. This has been changed, and
        this list now contains `node_id`s instead.
    */ 
    params.configKeys = ['groupedCardIds', 'sortedWidgetIds'];
    CardComponentViewModel.apply(this, [params]);

    var cards;
    if (params.state === 'report') {
        cards = flattenTree(params.pageVm.report.cards, []);
    } else {
        cards = !!params.card.parent ? params.card.parent.cards : flattenTree(params.card.topCards, []);
    }

    this.cardLookup = {};
    this.subscriptions = {};
    this.siblingCards = ko.observableArray();

    for (const card of cards) {
        this.cardLookup[card.model.id] = card;
        if (card.parentCard === params.card.parentCard &&
            card.model.cardinality() === '1' &&
            card !== params.card &&
            card.cards().length === 0) {
            this.siblingCards.push({'name': card.model.name(), 'id': card.model.id});
        }
    }

    this.groupedCards = ko.computed(function(){
        var gc = [this.card.model.id].concat(ko.toJS(this.groupedCardIds())).map(cardid => {
            var card = this.cardLookup[cardid]; 

            if (card) {
                var subscription = card.model.cardinality.subscribe(function(cardinality){
                    if (cardinality !== '1') {
                        card.model.cardinality('1');
                        var errorTitle = arches.translations.groupingErrorTitle;
                        var errorMesssage = arches.translations.groupingErrorMessage.replace(/\$\{cardName\}/g, self.card.model.name());
                        params.pageVm.alert(new AlertViewModel('ep-alert-red', errorTitle, errorMesssage, function(){}, function(){
                            var newgroup = ko.toJS(self.groupedCardIds()).filter(cardid => cardid !== card.model.id);
                            self.groupedCardIds(newgroup);
                            self.subscriptions[cardid].dispose();
                            card.model.cardinality('n');
                            self.card.model.save();
                        }));
                    }
                }, this);
                this.subscriptions[cardid] = subscription;
            }
            return card;
        });

        return gc;
    }, this);

    var updatedSortedWidgetsList = function(cards) {
        this.widgetInstanceDataLookup = {};

        var sortedWidgetIds = ko.toJS(this.sortedWidgetIds);
        var widgetNodeIdList = [];

        cards.forEach(function(card){
            if (card) {
                card.widgets().forEach(function(widget) {
                    this.widgetInstanceDataLookup[widget.node_id()] = widget;
                    widgetNodeIdList.push(widget.node_id());
                }, this);
            }
        }, this);

        _.each(this.widgetInstanceDataLookup, function(widget, widgetid) {
            if(!(_.contains(sortedWidgetIds, widgetid))) {
                sortedWidgetIds.push(widgetid);
            }
        }, this);

        this.sortedWidgetIds([
            ..._.without(sortedWidgetIds, ..._.difference(sortedWidgetIds, widgetNodeIdList))
        ]);
    };

    updatedSortedWidgetsList.call(this, this.groupedCards());

    this.groupedCards.subscribe(function(cards) {
        updatedSortedWidgetsList.call(this, cards);
    }, this);

    _.each(this.groupedCards(), function(card) {
        if (card) {
            card.widgets.subscribe(function() {
                updatedSortedWidgetsList.call(this, this.groupedCards());
            }, this);
        }
    }, this);

    if (!!params.preview) {
        _.each(this.groupedCards(), function(card) {
            if (card) {
                if (card.tiles().length === 0) {
                    card.tiles.push(card.getNewTile());
                }
                // we do this so that when you select a grouped widget
                // the selectedCard remains the same and doesn't jump to it's true card
                _.each(card.widgets(), function(widget) {
                    widget.parent = self.card;
                });
            }
        }, this);
    }

    this.groupedTiles = ko.computed(function() {
        if (this.saving()) {
            return this.tiles;
        } else {
            var tiles = [];
            _.each(this.groupedCards(), function(card) {
                if (card) {
                    if (card.tiles().length > 0) {
                        tiles.push(card.tiles()[0]);
                    } else {
                        tiles.push(card.getNewTile());
                    }
                }
            }, this);
            this.tiles = tiles;
            return tiles;
        }
    }, this);
    if (ko.isObservable(params.tiles)) {
        params.tiles(self.groupedTiles());

        self.groupedTiles.subscribe(function(tiles) {
            params.tiles(tiles);
        });
    }

    this.hasTiles = ko.computed(function() {
        return _.some(this.groupedCards(), function(card) {
            return card && card.tiles().length > 0;
        }, this);
    }, this);

    this.getDataForDisplay = function(nodeId) {
        var widget = self.widgetInstanceDataLookup[nodeId];
        var tile = self.groupedTiles().find(function(tile) {
            return Object.keys(tile.data).includes(widget.node.nodeid);
        });

        var ret = {
            widget: widget,
            tile: tile,
            tileData:  tile.data[widget.node.nodeid],
            card: self.cardLookup[widget.card.cardid()]
        };
        return ret;
    };

    this.beforeMove = function(e) {
        // do nothing
    };

    this.afterMove = function(e) {
        params.card.model.save();
    };

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
        return Boolean(_.find(self.groupedTiles(), function(tile) {
            return tile.dirty();
        }));
    });
    if (ko.isObservable(params.dirty)) {
        this.dirty.subscribe(function(dirty) {
            params.dirty(dirty);
        });
    }

    this.previouslySaved = ko.computed(function() {
        return !!(_.find(this.groupedTiles(), function(tile) {
            return !!tile.tileid;
        }, this));
    }, this);

    this.saveTiles = function(){
        var errors = ko.observableArray().extend({ rateLimit: 250 });
        var tiles = self.groupedTiles();
        var tile = self.groupedTiles()[0];
        tile.resourceinstance_id = ko.unwrap(self.form.resourceId);
        tile.transactionId = params.form?.workflowId;
        self.saving(true);

        tile.save(function(response) {
            errors.push(response);
            self.groupedCardIds.valueHasMutated();
            self.selectGroupCard();
        }, function(){
            var requests = _.map(_.rest(tiles), function(tile) {
                tile.resourceinstance_id = ko.unwrap(self.form.resourceId);
                tile.transactionId = params.form?.workflowId;
                return tile.save(function(response) {
                    errors.push(response);
                });
            }, self);
            Promise.all(requests).finally(function(){
                self.groupedCardIds.valueHasMutated();
                self.selectGroupCard();
                if (params.form.onSaveSuccess) {
                    params.form.onSaveSuccess(self.tiles);
                }
                self.saving(false);
                self.loading(false);
            });
        });
        errors.subscribe(function(errors){
            var title = [];
            var message = [];
            errors.forEach(function(response) {
                title.push(response.responseJSON.title);
                message.push(response.responseJSON.message);
            });
            params.pageVm.alert(new AlertViewModel('ep-alert-red', title.join(), message.join(), null, function(){}));
            if (params.form.onSaveError) {
                params.form.onSaveError(self.tile);
            }
        });
    };

    if (params.save) {
        params.save = self.saveTiles;
    }
    if (params.form && params.form.save) {
        params.form.save = self.saveTiles;
    }

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
            self.resetTiles();
        });
        errors.subscribe(function(errors){
            var title = [];
            var message = [];
            errors.forEach(function(response) {
                title.push(response.responseJSON.title);
                message.push(response.responseJSON.message);
            });
            params.pageVm.alert(new AlertViewModel('ep-alert-red', title.join(), message.join(), null, function(){}));
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
}

ko.components.register('grouping-card-component', {
    viewModel: viewModel,
    template: groupingCardTemplate,
});
export default viewModel;
