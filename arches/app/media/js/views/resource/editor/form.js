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
            this.ready = ko.observable(false);
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
                    self.ready(true);
                    if(callback){
                        callback(response);
                    }
                }
            });
        },

        /**
         * a function to return the knockout context used to render the actual widgets in the form
         * @memberof Form.prototype
         * @param  {object} outerCard a reference to the outer most card in the form
         * @param  {object} card a reference to the card associated with the form being rendered
         * @param  {object} tile a reference to the currently bound tile
         * @return {null} 
         */
        getFormEditingContext: function(outerCard, card, tile){
            if(outerCard.isContainer()){
                // this is not a "wizard"
                if(outerCard.get('cardinality')() === '1'){
                    if(card.get('cardinality')() === '1'){
                        //console.log(1)
                        return tile.tiles[card.get('nodegroup_id')]()[0];
                    }else{
                        //console.log(2)
                        return this.blanks[card.get('nodegroup_id')];
                    }
                } 
                // this is a "wizard"
                if(outerCard.get('cardinality')() === 'n'){
                    if(card.get('cardinality')() === '1'){
                        //console.log(3)
                        return tile.tiles[card.get('nodegroup_id')]()[0];
                    }else{
                        //console.log(4)
                        return this.blanks[card.get('nodegroup_id')];
                    }
                } 
            }else{
                // this is not a "wizard"
                if(outerCard.get('cardinality')() === '1'){
                    //console.log(5)
                    return tile;
                }else{
                    //console.log(6)
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
            var node = card.get('widgets')()[index].node;
            var name = node.name;
            var value = tile.data[node.nodeid];
            return {'name': name, 'value': value}
        },

        /**
         * saves a new tile object back to the database and adds it to the UI, in some instances it will 
         * save the outer most tile if that doesn't already exist
         * @memberof Form.prototype
         * @param  {object} parentTile a reference to the outer most tile, used to determine if that tile needs to be saved instead
         * @param  {boolean} [justadd=false] if true, then just adds a tile without saving it to the database
         * @param  {object} tile the tile to add/save
         * @return {null} 
         */
        saveTile: function(parentTile, justadd, tile){
            var savingParentTile = parentTile.tiles[tile.nodegroup_id()]().length === 0 && !parentTile.formid;
            var tiles = parentTile.tiles[tile.nodegroup_id()];
            if(!!parentTile.tileid){
                tile.parenttile_id(parentTile.tileid());
            }
            if(justadd){
                tiles.unshift(koMapping.fromJS(ko.toJS(tile)));
                this.clearTileValues(tile);
            }else{
                var model;
                // if the parentTile has never been saved then we need to save it instead, else just save the inner tile
                if(savingParentTile){
                    model = new TileModel(koMapping.toJS(parentTile));
                    model.get('tiles')[tile.nodegroup_id()].push(koMapping.toJS(tile));
                }else{
                    model = new TileModel(koMapping.toJS(tile))
                }
                model.save(function(request, status, model){
                    if(request.status === 200){
                        // if we had to save an parentTile
                        if(savingParentTile){
                            parentTile.tileid(request.responseJSON.tileid);
                            request.responseJSON.tiles[tile.nodegroup_id()].forEach(function(tile){
                                parentTile.tiles[tile.nodegroup_id].unshift(koMapping.fromJS(tile));
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
         * @param  {object} parentTile a the outer most tile to save
         * @return {null} 
         */
        saveTileGroup: function(parentTile, e){
            var model = new TileModel(koMapping.toJS(parentTile));
            model.save(function(request, status, model){
                if(request.status === 200){
                    this.tiles[parentTile.nodegroup_id()].unshift(koMapping.fromJS(request.responseJSON));
                    this.clearTile(parentTile);
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
            var model = new TileModel(ko.toJS(tile));
            model.save(function(request, status, model){
                if(request.status === 200){
                    tile.tileid(request.responseJSON.tileid);
                }else{
                    // inform the user
                }
            }, this);
        },

        /**
         * deletes a tile object or tile collection from the database and removes it from the UI
         * @memberof Form.prototype
         * @param  {object} parentTile a reference to the outer most tile that the tile to delete belongs to
         * @param  {object} tile the tile to delete
         * @return {null} 
         */
        deleteTile: function(parentTile, tile){
            var model;
            var deletingParentTile = parentTile.tiles[tile.nodegroup_id()]().length === 1 && !parentTile.formid;
            if(deletingParentTile){
                model = new TileModel(ko.toJS(parentTile));
            }else{
                model = new TileModel(ko.toJS(tile));
            }
            model.delete(function(request, status, model){
                if(request.status === 200){
                    if(deletingParentTile){
                        parentTile.tileid(null);
                        parentTile.tiles[tile.nodegroup_id()].remove(tile);
                    }else{
                        parentTile.tiles[tile.nodegroup_id()].remove(tile);
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
         * @param  {object} data a knockout reference to current context object
         * @param  {object} e event object
         * @return {null} 
         */
        toggleTile: function(data, e){
            $(e.currentTarget.nextElementSibling).toggle('fast');
        },

        /**
         * toggle the visiblity of the tile group in the view
         * @memberof Form.prototype
         * @param  {object} data a knockout reference to current context object
         * @param  {object} e event object
         * @return {null} 
         */
        toggleGroup: function(data, e){
            $(e.currentTarget.parentElement.parentElement.nextElementSibling).toggle('fast');
        },

        /**
         * Selects the appropriate tab in the form
         * @memberof Form.prototype
         * @param  {object} data a knockout reference to the current context object
         * @param  {object} e event object
         * @return {null} 
         */
        selectTab: function(data, e){
            var selectedTab = e.currentTarget;
            var tabElems = selectedTab.parentElement.children;
            var contentElems = selectedTab.parentElement.nextElementSibling.children;
            var tabIndex = Array.prototype.indexOf.call(tabElems, selectedTab);
            $(tabElems).removeClass('active');
            $(selectedTab).addClass('active');
            $(contentElems).removeClass('active in');
            $(contentElems[tabIndex]).addClass('active in');
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
