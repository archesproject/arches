define([
    'jquery',
    'backbone',
    'knockout',
    'knockout-mapping',
    'arches',
    'widgets',
    'models/card',
    'models/tile',
    'resource-editor-data',
    'select2',
    'bindings/let'
], function($, Backbone, ko, koMapping, arches, widgets, CardModel, TileModel, data) {
    var FormView = Backbone.View.extend({
        /**
        * A backbone view representing a card form preview
        * @augments Backbone.View
        * @constructor
        * @name FormView
        */

        /**
        * Initializes the view with optional parameters
        * @memberof FormView.prototype
        */
        initialize: function(options) {
            var self = this;
            this.formid = options.formid;
            this.resourceid = options.resourceid;
            this.widgetLookup = widgets;
            this.cards = ko.observableArray([new CardModel({})]);
            this.tiles = koMapping.fromJS({});
            this.blanks = koMapping.fromJS({});
            this.loadForm(this.formid);
        },

        loadForm: function(formid, callback){
            var self = this;
            $.ajax({
                type: "GET",
                url: arches.urls.resource_data.replace('//', '/' + this.resourceid + '/') + formid,
                success: function(response) {
                    window.location.hash = formid;
                    koMapping.fromJS(response.tiles, self.tiles);
                    koMapping.fromJS(response.blanks, self.blanks);
                    self.cards.removeAll();
                    response.forms[0].cardgroups.forEach(function(cardgroup){
                        self.cards.push(new CardModel({
                            data: cardgroup,
                            datatypes: data.datatypes
                        }));
                    },this);
                },
                error: function(response) {

                },
                complete: function(response){
                    if(callback){
                        callback(response)
                    }
                }
            });
        },

        // getTileData: function(outterCard, card, forceblank){
        //     var nodegroup_id = card.get('nodegroup_id');
        //     var cardinaltiy = card.get('cardinality')();
        //     var forceblank = outterCard.get('cardinality')() === 'n' || 
        //         (outterCard.get('cardinality')() === '1' && cardinaltiy === 'n');

        //     if(outterCard.get('cardinality')() === 'n'){
        //         return this.blanks[outterCard.get('nodegroup_id')];
        //     }
        //     if(cardinaltiy === '1'){
        //         if(nodegroup_id){
        //             if(card.get('tiles')().length === 0){
        //                 return this.blanks[nodegroup_id];
        //             }else{
        //                 return card.get('tiles')()[0];
        //             } 
        //         }else{
        //             return new TileModel();
        //         }
        //     }
        //     if(cardinaltiy === 'n'){
        //         if(nodegroup_id){
        //             if(forceblank){
        //                 return this.blanks[nodegroup_id];
        //             }else{
        //                 return card.get('tiles')[nodegroup_id]();
        //             }
        //         }else{
        //             return new TileModel();
        //         }
        //     }
        // },

        getFormEditingContext: function(outterCard, card, tile){
            if(outterCard.isContainer()){
                if(outterCard.get('cardinality')() === '1'){
                    if(card.get('cardinality')() === '1'){
                        if(Object.getOwnPropertyNames(tile.data).length === 0){
                            tile.data = this.blanks[card.get('nodegroup_id')].data;
                        }
                        return tile;
                    }else{
                        return this.blanks[card.get('nodegroup_id')];
                    }
                } 
                if(outterCard.get('cardinality')() === 'n'){
                    if(card.get('cardinality')() === '1'){
                        return form.blanks[card.get('nodegroup_id')];
                    }else{

                    }
                } 
            }else{
                if(outterCard.get('cardinality')() === '1'){
                    if(Object.getOwnPropertyNames(tile.data).length === 0){
                        tile.data = this.blanks[card.get('nodegroup_id')].data;
                    }
                    return tile;
                }else{
                    return this.blanks[card.get('nodegroup_id')];
                }
            }

            //return outterCard.get('cardinality')() === 'n' ? (tile.tiles[card.get('nodegroup_id')]().length > 0 ? tile.tiles[card.get('nodegroup_id')]()[0] : form.blanks[card.get('nodegroup_id')]) : tile;
        },

        getTileList: function(outterCard, card){
            var nodegroup_id = card.get('nodegroup_id');
            var cardinaltiy = card.get('cardinality')();
            var forceblank = outterCard.get('cardinality')() === 'n'; //|| 
                //(outterCard.get('cardinality')() === '1' && cardinaltiy === 'n');
            if(outterCard.get('cardinality')() === 'n' && card && forceblank){
                return this.blanks[nodegroup_id];
            }
            return card.get('tiles')();

            // if(cardinaltiy === '1'){
            //     if(nodegroup_id){
            //         if(card.get('tiles')().length === 0){
            //             return this.blanks[nodegroup_id];
            //         }else{
            //             return card.get('tiles')()[0];
            //         } 
            //     }else{
            //         return new TileModel();
            //     }
            // }
            // if(cardinaltiy === 'n'){
            //     if(nodegroup_id){
            //         if(forceblank){
            //             return this.blanks[nodegroup_id];
            //         }else{
            //             return card.get('tiles')[nodegroup_id]();
            //         }
            //     }else{
            //         return new TileModel();
            //     }
            // }
        },

        getNodeValueAndLabel: function(index, tile, card){
            console.log(tile);
            var node = card.get('widgets')()[index].node;
            var name = node.name;
            var value = tile.data[node.nodeid];
            return {'name': name, 'value': value}
        },

        /**
         * saves a new tile object back to the database and adds it to the tilegroup
         * @memberof Form.prototype
         * @param  {object} card the card the new tile should belong to
         * @param  {object} tile the tile to add/save
         * @param  {boolean} [justadd=false] if true, then just adds a tile without saving it to the database
         * @return {null} 
         */
        saveTile: function(card, tile, justadd){
            console.log(koMapping.toJS(tile));
            var nodegroup_id = tile.nodegroup_id();
            var tiles = card.get('tiles');
            if(justadd){
                tiles.unshift(koMapping.fromJS(ko.toJS(tile)));
                this.clearTile(tile);
            }else{
                var model = new TileModel(koMapping.toJS(tile));
                model.save(function(request, status, model){
                    if(request.status === 200){
                        // if(!(nodegroup_id in tiles)){
                        //     tiles[nodegroup_id] = koMapping.fromJS([]);
                        // }
                        // tiles[nodegroup_id].unshift(koMapping.fromJS(request.responseJSON));
                        tiles.unshift(koMapping.fromJS(request.responseJSON));
                        this.clearTile(tile);
                    }else{
                        // inform the user
                    }
                }, this);
            }
        },

        saveTile2: function(outterTile, justadd, tile){
            console.log(koMapping.toJS(tile));
            var savingOutterTile = !outterTile.tileid();
            var tiles = outterTile.tiles[tile.nodegroup_id()];
            tile.parenttile_id(outterTile.tileid());
            if(justadd){
                tiles.unshift(koMapping.fromJS(ko.toJS(tile)));
                this.clearTile(tile);
            }else{
                var model;
                // if the outterTile has never been saved then we need to save it instead, else just save the inner tile
                if(savingOutterTile){
                    model = new TileModel(koMapping.toJS(outterTile));
                    model.get('tiles')[tile.nodegroup_id()].push(koMapping.toJS(tile));
                }else{
                    model = new TileModel(koMapping.toJS(tile))
                }
                model.save(function(request, status, model){
                    if(request.status === 200){
                        // if we had to save an outterTile
                        if(savingOutterTile){
                            // koMapping.fromJS(request.responseJSON, outterTile);
                            outterTile.tileid(request.responseJSON.tileid);
                            request.responseJSON.tiles[tile.nodegroup_id()].forEach(function(tile){
                                outterTile.tiles[tile.nodegroup_id].unshift(koMapping.fromJS(tile));
                            }, this)
                        }else{
                            tiles.unshift(koMapping.fromJS(request.responseJSON));
                        }
                        this.clearTile(tile);
                    }else{
                        // inform the user
                    }
                }, this);
            }
        },

        saveTileGroup: function(tilegroup, justadd, cardcontainer, e){
            console.log(koMapping.toJS(cardcontainer));
            var parentTile = this.getTileData(cardcontainer, true);
            cardcontainer.get('cards')().forEach(function(card){
                parentTile.tiles[card.get('nodegroup_id')] = card.get('tiles')();
            }, this);

            var model = new TileModel(koMapping.toJS(parentTile));
            model.save(function(request, status, model){
                if(request.status === 200){
                    tilegroup.unshift(koMapping.fromJS(request.responseJSON));
                    
                    _.each(cardcontainer.get('tiles'), function(tile){
                        this.clearTile(tile);
                    }, this);
                    cardcontainer.get('tiles').removeAll();

                    _.each(cardcontainer.get('cards'), function(card){
                        _.each(card.get('tiles'), function(tile){
                            this.clearTile(tile);
                        }, this);
                    }, this);
                }else{
                    // inform the user
                }
            }, this);
        },

        /**
         * saves the contents of an existing tile object back to the database
         * @memberof Form.prototype
         * @param  {object} tile the tile to save
         * @param  {object} e event object
         * @return {null} 
         */
        updateTile: function(tile, e){
            console.log(ko.toJS(tile));
            var model = new TileModel(ko.toJS(tile));
            model.save(function(request, status, model){
                if(request.status === 200){
                    // inform the user???
                }else{
                    // inform the user
                }
            }, this);
        },

        /**
         * deletes a tile object from the database and removes it from the tilegroup
         * @memberof Form.prototype
         * @param  {object} card a reference to the card that the tile being deleted belongs to
         * @param  {object} tile the tile to delete
         * @return {null} 
         */
        deleteTile: function(outterTile, tile){
            console.log(ko.toJS(tile));
            var model;
            var deletingOutterTile = outterTile.tiles[tile.nodegroup_id()]().length === 1;
            if(deletingOutterTile){
                model = new TileModel(ko.toJS(outterTile));
            }else{
                model = new TileModel(ko.toJS(tile));
            }
            model.delete(function(request, status, model){
                if(request.status === 200){
                    if(deletingOutterTile){
                        outterTile.tileid(null);
                        outterTile.tiles[tile.nodegroup_id()].remove(tile);
                    }else{
                        outterTile.tiles[tile.nodegroup_id()].remove(tile);
                    }
                }else{
                    // inform the user
                }
            }, this);
        },
        
        /**
         * currently unused
         * @memberof Form.prototype
         * @param  {object} data a knockout reference to the tile object
         * @param  {object} e event object
         * @return {null} 
         */
        cancelEdit: function(data, e){
            console.log(ko.toJSON(data));
        },

        /**
         * toggle the visiblity of the tile in the view
         * @memberof Form.prototype
         * @param  {object} data a knockout reference to the tile object
         * @param  {object} e event object
         * @return {null} 
         */
        toggleTile: function(data, e){
            //$('#abc'+data.tileid()).toggle('fast');
            $(e.currentTarget.nextElementSibling).toggle('fast');
        },

        /**
         * removes any existing values set on the tile
         * @memberof Form.prototype
         * @param  {object} tile the tile to remove values from
         * @return {null} 
         */
        clearTile: function(tile){
            _.each(tile.data, function(value, key, list){
                value("");
            }, this);
            _.each(tile.tiles, function(value, key, list){
                value.removeAll();
            }, this);

            // _.each(card.get('tiles'), function(tile){
            //     _.each(tile.data, function(value, key, list){
            //         value("");
            //     }, this);
            // }, this);
            // card.get('tiles').removeAll();

            // _.each(card.get('cards'), function(card){
            //     this.clearTile(card);
            // }, this);
        }

    });
    return FormView;
});
