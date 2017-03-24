define([
    'jquery',
    'backbone',
    'knockout',
    'knockout-mapping',
    'arches',
    'widgets',
    'models/card',
    'models/tile',
    'models/graph',
    'resource-editor-data',
    'select2',
    'bindings/let',
    'bindings/sortable',
    //'plugins/ko-reactor.min'
], function($, Backbone, ko, koMapping, arches, widgets, CardModel, TileModel, GraphModel, data) {
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
            this.ready = ko.observable(false);
            this.formTiles = ko.observableArray();
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
            self.graph = new GraphModel({data: data.graph});
            $.ajax({
                type: "GET",
                url: arches.urls.resource_data.replace('//', '/' + this.resourceid + '/') + formid,
                success: function(response) {
                    window.location.hash = formid;
                    self.formTiles.removeAll();
                    self.ready(false);
                    koMapping.fromJS(response.tiles, self.tiles);
                    koMapping.fromJS(response.blanks, self.blanks);
                    self.initTiles(self.tiles);
                    self.initTiles(self.blanks);


                    // ko.watch({blanks: self.blanks, tiles: self.tiles}, {
                    //     depth: -1,
                    //     keepOldValues: 1,
                    //     tagParentsWithName: true,
                    //     tagFields: false,
                    //     oldValues: 3
                    // }, function(parents, child, item) {
                    //     var log = parents[0] ? parents[0]._fieldName + ': ' : '';

                    //     if (item)
                    //         log += item.status + ' ' + ko.toJSON(item.value);
                    //     else
                    //         log += ko.toJSON(child.oldValues[0]) + ' -> ' + ko.toJSON(child());
                    //         //log += ko.toJSON(child());
                    //     //parents[0]()[0].dirty(true);
                    //     console.log(log);
                    // });

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
         * initializes a list of tile objects
         * @memberof Form.prototype
         * @param  {object} data the list of tile objects to initialize
         * @return {null}
         */
        initTiles: function(data){
            _.keys(data).forEach(function(nodegroup_id){
                if(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(nodegroup_id)){
                    data[nodegroup_id]().forEach(function(tile){
                        this.initTile(tile);
                    }, this);
                }
            }, this);
            return data;
        },

        /**
         * initializes a single tile object
         * @memberof Form.prototype
         * @param  {object} tile the tile object to initialize
         * @return {null}
         */
        initTile: function(tile){
            if('tiles' in tile && _.keys(tile.tiles).length > 0){
                tile.dirty = ko.observable(false);
            }else{
                tile._data = ko.observable(koMapping.toJSON(tile.data));
                tile.dirty = ko.computed(function(){
                    return !_.isEqual(JSON.parse(tile._data()), JSON.parse(koMapping.toJSON(tile.data)));
                });
            }
            if(!!tile.tiles){
                this.initTiles(tile.tiles);
            }
            tile.formData = new FormData();
            this.formTiles.push(tile);
            return tile;
        },

        /**
         * gets a copy of a new blank tile
         * @memberof Form.prototype
         * @param  {string} nodegroup_id the nodegroup id of the blank tile to retrieve
         * @return {object} a tile object
         */
        getBlankTile: function(nodegroup_id){
            var tile = koMapping.fromJS(koMapping.toJS(this.blanks[nodegroup_id]()[0]));
            this.initTile(tile);
            return tile;
        },

        /**
         * a function to return the knockout context used to render the actual widgets in the form
         * @memberof Form.prototype
         * @param  {object} outerCard a reference to the outer most card in the form
         * @param  {object} card a reference to the card associated with the form being rendered
         * @param  {object} tile a reference to the currently bound tile
         * @return {object} a tile object
         */
        getFormEditingContext: function(outerCard, card, tile){
            if(outerCard.isContainer()){
                // this is not a "wizard"
                if(outerCard.get('cardinality')() === '1'){
                    if(card.get('cardinality')() === '1'){
                        //console.log(1)
                        if(tile.tiles[card.get('nodegroup_id')]().length === 0){
                            return ko.ignoreDependencies(this.getBlankTile, this, [card.get('nodegroup_id')]);
                        }else{
                            return tile.tiles[card.get('nodegroup_id')]()[0];
                        }
                    }else{
                        //console.log(2)
                        return ko.ignoreDependencies(this.getBlankTile, this, [card.get('nodegroup_id')]);
                    }
                }
                // this is a "wizard"
                if(outerCard.get('cardinality')() === 'n'){
                    if(card.get('cardinality')() === '1'){
                        //console.log(3)
                        if(tile.tiles[card.get('nodegroup_id')]().length === 0){
                            return ko.ignoreDependencies(this.getBlankTile, this, [card.get('nodegroup_id')]);
                        }else{
                            return tile.tiles[card.get('nodegroup_id')]()[0];
                        }
                    }else{
                        //console.log(4)
                        return ko.ignoreDependencies(this.getBlankTile, this, [card.get('nodegroup_id')]);
                    }
                }
            }else{
                // this is not a "wizard"
                if(outerCard.get('cardinality')() === '1'){
                    //console.log(5)
                    return tile;
                }else{
                    //console.log(6)
                    return ko.ignoreDependencies(this.getBlankTile, this, [card.get('nodegroup_id')]);
                }
            }
        },

        /**
         * saves a new tile object back to the database and adds it to the UI, in some instances it will
         * save the outer most tile if it doesn't already exist
         * @memberof Form.prototype
         * @param  {object} parentTile a reference to the outer most tile, used to determine if that tile needs to be saved as well
         * @param  {boolean} cardinality the cardinality code of the tile being managed (1-, n-, 1-1, 1-n, n-1, n-n)
         * @param  {object} tile the tile to add/save
         * @return {null}
         */
        saveTile: function(parentTile, cardinality, tile){
            var tiles = parentTile.tiles[tile.nodegroup_id()];
            var tileHasParent = cardinality === '1-1' ||
                                cardinality === '1-n' ||
                                cardinality === 'n-1' ||
                                cardinality === 'n-n';
            if(tileHasParent){
                tile.parenttile_id(parentTile.tileid());
            }
            if(cardinality === 'n-n' && !parentTile.tileid()){
                parentTile.dirty(true);
                tiles.push(this.initTile(koMapping.fromJS(ko.toJS(tile))));
                this.clearTile(tile);
            }else{
                var model;
                var savingParentTile = false;
                var updatingTile = false;
                if(tileHasParent && !parentTile.tileid()){
                    savingParentTile = true;
                }
                if(cardinality === '1-' || cardinality === '1-1' || cardinality === 'n-1' ||
                  (cardinality === 'n-n' && !!tile.tileid()) ||
                  (cardinality === 'n-' && !!tile.tileid()) ||
                  (cardinality === '1-n' && !!tile.tileid())){
                    updatingTile = true;
                }

                // console.log('cardinality: ' + cardinality)
                // console.log('savingParentTile: ' + savingParentTile)
                // console.log('updatingTile: ' + updatingTile)

                // if the parentTile has never been saved then we need to save it instead, else just save the inner tile
                if(savingParentTile){
                    var tilemodel = {};
                    tilemodel[tile.nodegroup_id()] = [koMapping.toJS(tile)];
                    model = new TileModel(koMapping.toJS(parentTile));
                    model.set('tiles', tilemodel);
                }else{
                    model = new TileModel(koMapping.toJS(tile))
                }
                this.trigger('before-update');
                model.save(function(response, status, model){
                    if(response.status === 200){
                        // if we had to save an parentTile
                        console.log(response.responseJSON)
                        if(updatingTile){
                            var updatedTileData;
                            if(savingParentTile){
                                if(response.responseJSON.tiles[tile.nodegroup_id()].length > 1){
                                    throw('Error: tile has multiple parents');
                                }
                                parentTile.tileid(response.responseJSON.tileid);
                                updatedTileData = response.responseJSON.tiles[tile.nodegroup_id()][0];

                            }else{
                                updatedTileData = response.responseJSON;
                            }

                            tile.tileid(updatedTileData.tileid);
                            tile.parenttile_id(updatedTileData.parenttile_id);
                            if(!!tile._data()){
                                tile._data(JSON.stringify(updatedTileData.data));
                            }
                        }else{
                            if(savingParentTile){
                                parentTile.tileid(response.responseJSON.tileid);
                                response.responseJSON.tiles[tile.nodegroup_id()].forEach(function(tile){
                                    parentTile.tiles[tile.nodegroup_id].push(this.initTile(koMapping.fromJS(tile)));
                                }, this);
                            }else{
                                tiles.push(this.initTile(koMapping.fromJS(response.responseJSON)));
                            }
                            this.clearTile(tile);
                        }
                    }
                    this.trigger('after-update', response, tile);
                }, this, tile.formData);
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
            this.trigger('before-update');
            model.save(function(response, status, model){
                if(response.status === 200){
                    this.tiles[parentTile.nodegroup_id()].push(this.initTile(koMapping.fromJS(response.responseJSON)));
                    this.clearTile(parentTile);
                }
                this.trigger('after-update', response, parentTile);
            }, this, parentTile.formData);
        },

        /**
         * deletes a tile object or tile collection from the database and removes it from the UI
         * @memberof Form.prototype
         * @param  {object} parentTile a reference to the outer most tile that the tile to delete belongs to
         * @param  {object} tile the tile to delete
         * @param  {boolean} justremove if true, remove without deleting, else delete from the database
         * @param  {boolean} cardinality the cardinality code of the tile being managed (1-, n-, 1-1, 1-n, n-1, n-n)
         * @return {null}
         */
        deleteTile: function(parentTile, tile, justremove, cardinality){
            var tiles = parentTile.tiles[tile.nodegroup_id()];
            var tileHasParent = cardinality === '1-1' ||
                                cardinality === '1-n' ||
                                cardinality === 'n-1' ||
                                cardinality === 'n-n';
            if(justremove){
                tiles.remove(tile);
                if(tiles().length === 0){
                    parentTile.dirty(false);
                }
            }else{
                var model;
                var deletingParentTile = tileHasParent; //tiles().length === 1 && !parentTile.formid;
                if(tileHasParent){
                    _.each(parentTile.tiles, function(t){
                        if(t().length !== 1){
                            deletingParentTile = false;
                        }else{
                            if(!_.isEqual(JSON.parse(koMapping.toJSON(t()[0])), JSON.parse(koMapping.toJSON(tile)))){
                                if(!!t()[0].tileid() || !!t()[0].parenttile_id()){
                                    deletingParentTile = false;
                                }
                            }
                        }
                    })
                }
                if(deletingParentTile){
                    model = new TileModel(ko.toJS(parentTile));
                }else{
                    model = new TileModel(ko.toJS(tile));
                }
                this.trigger('before-update');
                model.delete(function(response, status, model){
                    if(response.status === 200){
                        tiles.remove(tile);
                        if(deletingParentTile){
                            parentTile.tileid('');
                            this.tiles[parentTile.nodegroup_id()].remove(parentTile);
                        }
                    }
                    this.trigger('after-update', response, tile);
                }, this);
            }
        },

        /**
         * deletes a tile collection from the database and removes it from the UI
         * @memberof Form.prototype
         * @param  {object} parentTile a reference to the tile to delete
         * @return {null}
         */
        deleteTileGroup: function(parentTile, e){
            model = new TileModel(ko.toJS(parentTile));
            this.trigger('before-update');
            model.delete(function(response, status, model){
                if(response.status === 200){
                    this.tiles[parentTile.nodegroup_id()].remove(parentTile);
                }
                this.trigger('after-update', response, parentTile);
            }, this);
        },

        /**
         * updates the sort order of tiles
         * @memberof Form.prototype
         * @return {null}
         */
        reorderTiles: function (tiles) {
            var self = this;
            this.trigger('before-update');
            $.ajax({
                type: "POST",
                data: JSON.stringify({
                    tiles: koMapping.toJS(tiles)
                }),
                url: arches.urls.reorder_tiles,
                complete: function(response) {
                    self.trigger('after-update', response);
                }
            });
        },

        /**
         * undo unsaved edits and return tile data to it's previous state
         * @memberof Form.prototype
         * @param  {object} tile a knockout reference to the tile object
         * @param  {object} e event object
         * @return {null}
         */
        cancelEdit: function(parentTile, tile, e){
            var oldData = JSON.parse(tile._data());
            var self = this;
            _.keys(tile.data).forEach(function(nodegroup_id){
                if(/^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(nodegroup_id)){
                    if (ko.isObservable(tile.data[nodegroup_id])) {
                      tile.data[nodegroup_id](oldData[nodegroup_id]);
                    } else {
                      _.keys(tile.data[nodegroup_id]).forEach(function(key){
                        if (ko.isObservable(tile.data[nodegroup_id][key])) {
                          tile.data[nodegroup_id][key](oldData[nodegroup_id][key])
                        }
                      }, this)
                    }
                    self.trigger('tile-reset', tile);
                }
            }, this);
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
            window.setTimeout(function(){window.dispatchEvent(new Event('resize'))},200) //ensures the map expands to the extent of its container element
        },

        /**
         * toggle the visiblity of the tile group in the view
         * @memberof Form.prototype
         * @param  {object} data a knockout reference to current context object
         * @param  {object} e event object
         * @return {null}
         */
        toggleGroup: function(data, e){
            var contentPane = $(e.currentTarget.nextElementSibling);
            contentPane.toggle('fast');
            $(contentPane.find('.library-tools-icon')[0]).toggle('fast');
            window.setTimeout(function(){window.dispatchEvent(new Event('resize'))},200) //ensures the map expands to the extent of its container element
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
            var contentElems = $(selectedTab.parentElement.nextElementSibling).find('.tab-pane');
            var tabIndex = Array.prototype.indexOf.call(tabElems, selectedTab);
            $(tabElems).removeClass('active');
            $(selectedTab).addClass('active');
            $(contentElems).removeClass('active in');
            $(contentElems[tabIndex]).addClass('active in');
            e.stopPropagation();
        },

        /**
         * removes any existing values set on the tile as well as removing any child tile instances
         * @memberof Form.prototype
         * @param  {object} tile the tile to remove values from
         * @return {null}
         */
        clearTile: function(tile){
            // clear any child tile instances
            _.each(tile.tiles, function(innerTile, nodegroup_id, list){
                if(this.getTileCardinality(nodegroup_id) === '1'){
                    _.each(innerTile(), function(tile){
                        this.clearTile(tile);
                    }, this);

                }else{
                    innerTile.removeAll();
                }
            }, this);

            // clear any data on the tile itself
            _.each(tile.data, function(value, key, list){
                value(null);
            }, this);

            // we have to manage the parent dirty state directly
            if(ko.isObservable(tile.dirty) && !ko.isComputed(tile.dirty)){
                tile.dirty(false);
            }
        },

        /**
         * finds the cardinality of a given nodegroup
         * @memberof Form.prototype
         * @param  {string} nodegroup_id the id of the nodegroup
         * @return {string} either 'n' or '1', or '' if the cardinality wasn't found
         */
        getTileCardinality: function(nodegroup_id){
            var cardinality = '';
            var getCardinality = function(cards, nodegroup_id){
                cards().forEach(function(card){
                    if (card.get('nodegroup_id') === nodegroup_id){
                        cardinality = card.get('cardinality')();
                    }
                    getCardinality(card.get('cards'), nodegroup_id);
                })
            }
            getCardinality(this.cards, nodegroup_id);
            return cardinality;
        }
    });

    return FormView;
});
