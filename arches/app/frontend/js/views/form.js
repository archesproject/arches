define([
    'jquery',
    'backbone',
    'knockout',
    'knockout-mapping',
    'underscore'
], function ($, Backbone, ko, koMapping, _) {
    return Backbone.View.extend({
        /**
         * a view to manage the operations around saving tile data
         * @augments Backbone.View
         * @constructor
         * @name Form
         */

        /**
         * initialize the form with a passed in model reference
         * @memberof Form.prototype
         * @param  {object} options [description]
         * @param  {string} [options.modelName='tile'] name of the model use as the basis for the form
         * @return {null}
         */
        initialize: function(options) {
            var self = this;
            self.modelReady = ko.observable(false);
            require(['models/'+(options.modelName?options.modelName:'tile')], function (TileModel) {
                self.TileModel = TileModel;
                self.modelReady(true);
            })
            this.form = this.$el;

            // parse then restringify JSON data to ensure whitespace is identical
            this._rawdata = ko.toJSON(JSON.parse(this.form.find('#tiledata').val()));
            this.cardgroups = koMapping.fromJS(JSON.parse(this._rawdata));
            this.blanks = koMapping.fromJS(JSON.parse(this.form.find('#blanks').val()));

            this.tiles = koMapping.fromJS(JSON.parse(this._rawdata));

            console.log(JSON.parse(this._rawdata));
            console.log(koMapping.toJS(this.blanks));

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
            var nodegroup_id = tile.nodegroup_id();
            if(justadd === "true"){
                tilegroup.unshift(koMapping.fromJS(ko.toJS(tile)));
                this.clearTile(tile);
            }else{
                var model = new this.TileModel(koMapping.toJS(tile));
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
            var model = new this.TileModel(ko.toJS(tile));
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
            var model = new this.TileModel(ko.toJS(tile));
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
            $('#abc'+data.tileid()).toggle('fast');
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
});
