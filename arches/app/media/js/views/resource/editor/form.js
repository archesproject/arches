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

        getTileData: function(card, forceblank){
            var nodegroup_id = card.get('nodegroup_id');
            var cardinaltiy = card.get('cardinality')();
            if(cardinaltiy === '1'){
                if(nodegroup_id){
                    if(card.tiles[nodegroup_id]().length === 0){
                        return this.blanks[nodegroup_id];
                    }else{
                        return card.tiles[nodegroup_id]()[0];
                    } 
                }else{
                    return new TileModel();
                }
            }
            if(cardinaltiy === 'n'){
                if(nodegroup_id){
                    if(forceblank){
                        return this.blanks[nodegroup_id];
                    }else{
                        return card.tiles[nodegroup_id]();
                    }
                }else{
                    return new TileModel();
                }
            }
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
         * @param  {object} tilegroup a reference to the group of tiles being managed by this form
         * @param  {boolean} [justadd=false] if true, then just adds a tile without saving it to the database
         * @param  {object} tile the tile to add/save
         * @param  {object} e event object
         * @return {null} 
         */
        saveTile: function(tilegroup, justadd, tile, e){
            console.log(koMapping.toJS(tile));
            var nodegroup_id = tile.nodegroup_id();
            if(justadd === "true"){
                tilegroup.unshift(koMapping.fromJS(ko.toJS(tile)));
                this.clearTile(tile);
            }else{
                var model = new TileModel(koMapping.toJS(tile));
                model.save(function(request, status, model){
                    if(request.status === 200){
                        // if(!(nodegroup_id in tilegroup)){
                        //     tilegroup[nodegroup_id] = koMapping.fromJS([]);
                        // }
                        // tilegroup[nodegroup_id].unshift(koMapping.fromJS(request.responseJSON));
                        tilegroup.unshift(koMapping.fromJS(request.responseJSON));
                        this.clearTile(tile);
                    }else{
                        // inform the user
                    }
                }, this);
            }
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
         * @param  {object} tilegroup a reference to the group of tiles being managed by this form
         * @param  {object} tile the tile to add/save
         * @param  {object} e event object
         * @return {null} 
         */
        deleteTile: function(tilegroup, tile, e){
            console.log(ko.toJS(tile));
            var nodegroup_id = tile.nodegroup_id();
            var model = new TileModel(ko.toJS(tile));
            model.delete(function(request, status, model){
                if(request.status === 200){
                    tilegroup.remove(tile)
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
        }

    });
    return FormView;
});
