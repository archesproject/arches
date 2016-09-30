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

        /**
         * asynchronously loads a form into the UI
         * @memberof Form.prototype
         * @param  {object} formid the id of the form to load
         * @param  {object} callback called after the form loads
         * @return {null} 
         */
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

        /**
         * a function to return the knockout context used to render the actual widgets in the form
         * @memberof Form.prototype
         * @param  {object} outterCard a reference to the outter most card in the form
         * @param  {object} card a reference to the card associated with the form being rendered
         * @param  {object} tile a reference to the currently bound tile
         * @return {null} 
         */
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
                        return tile.tiles[card.get('nodegroup_id')]()[0];
                    }else{
                        return this.blanks[card.get('nodegroup_id')];
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
        },

        /**
         * a function to get the label and value of a widget at the given array index in the widget array
         * @memberof Form.prototype
         * @param  {integer} index the array index to use when locating the widget in question
         * @param  {object} tile a reference to the currently bound tile
         * @param  {object} card a reference to the card associated with the form being rendered
         * @return {'name': label associated with the widget, 'value': value of the data associated with that widget}
         */
        getNodeValueAndLabel: function(index, tile, card){
            console.log(tile);
            var node = card.get('widgets')()[index].node;
            var name = node.name;
            var value = tile.data[node.nodeid];
            return {'name': name, 'value': value}
        },

        /**
         * saves a new tile object back to the database and adds it to the UI, in some instances it will 
         * save the outter most tile if that doesn't already exist
         * @memberof Form.prototype
         * @param  {object} outterTile a reference to the outter most tile, used to determine if that tile needs to be saved instead
         * @param  {boolean} [justadd=false] if true, then just adds a tile without saving it to the database
         * @param  {object} tile the tile to add/save
         * @return {null} 
         */
        saveTile: function(outterTile, justadd, tile){
            console.log(koMapping.toJS(tile));
            var savingOutterTile = !outterTile.tileid();
            var tiles = outterTile.tiles[tile.nodegroup_id()];
            tile.parenttile_id(outterTile.tileid());
            if(justadd){
                tiles.unshift(koMapping.fromJS(ko.toJS(tile)));
                this.clearTileValues(tile);
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
                            this.clearTile(tile);
                        }else{
                            tiles.unshift(koMapping.fromJS(request.responseJSON));
                            this.clearTileValues(tile);
                        }
                    }else{
                        // inform the user
                    }
                }, this);
            }
        },

        /**
         * saves a tile and it's child tiles back to the database
         * @memberof Form.prototype
         * @param  {object} outterTile a the outter most tile to save
         * @return {null} 
         */
        saveTileGroup: function(outterTile, e){
            console.log(koMapping.toJS(outterTile));
            var model = new TileModel(koMapping.toJS(outterTile));
            model.save(function(request, status, model){
                if(request.status === 200){
                    this.tiles[outterTile.nodegroup_id()].unshift(koMapping.fromJS(request.responseJSON));
                    this.clearTile(outterTile);
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
         * deletes a tile object or tile collection from the database and removes it from the UI
         * @memberof Form.prototype
         * @param  {object} outterTile a reference to the outter most tile that the tile to delete belongs to
         * @param  {object} tile the tile to delete
         * @return {null} 
         */
        deleteTile: function(outterTile, tile){
            console.log(ko.toJS(tile));
            var model;
            var isTileGroup = !!outterTile.formid;
            var deletingOutterTile = outterTile.tiles[tile.nodegroup_id()]().length === 1;
            if(deletingOutterTile && !isTileGroup){
                model = new TileModel(ko.toJS(outterTile));
            }else{
                model = new TileModel(ko.toJS(tile));
            }
            model.delete(function(request, status, model){
                if(request.status === 200){
                    if(deletingOutterTile && !isTileGroup){
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
         * removes any existing values set on the tile as well as removing any child tile instances
         * @memberof Form.prototype
         * @param  {object} tile the tile to remove values from
         * @return {null} 
         */
        clearTile: function(tile){
            var card;
            this.cards().forEach(function(c){
                if(c.get('nodegroup_id') === tile.nodegroup_id()){
                    card = c;
                }
            }, this);

            if(!!card){
                card.get('cards')().forEach(function(innerCard){
                    if(innerCard.get('cardinality')() === 'n'){
                        _.each(tile.tiles, function(innerTile, nodegroup_id, list){
                            if(nodegroup_id === innerCard.get('nodegroup_id')){
                                innerTile.removeAll();
                            }
                        }, this);
                    }else{
                        _.each(tile.tiles, function(innerTile, nodegroup_id, list){
                            if(nodegroup_id === innerCard.get('nodegroup_id')){
                                this.clearTileValues(innerTile()[0]);
                            }
                        }, this);
                    }
                }, this);
            }
        },

        /**
         * removes any existing values set on the tile.data attribute
         * @memberof Form.prototype
         * @param  {object} tile the tile to remove values from
         * @return {null} 
         */
        clearTileValues: function(tile){
            _.each(tile.data, function(value, key, list){
                value("");
            }, this);
        }

    });
    return FormView;
});
