define([
    'jquery',
    'backbone',
    'knockout',
    'knockout-mapping',
    'underscore',
    'bindings/datepicker'
], function ($, Backbone, ko, koMapping, _) {
    return Backbone.View.extend({

        initialize: function(opts) {
            var self = this;
            self.modelReady = ko.observable(false);
            require(['models/'+(opts.modelName?opts.modelName:'tile')], function (TileModel) {
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

        saveTile: function(tilegroup, justadd, tile, e){
            console.log(koMapping.toJS(tile));
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

        cancelEdit: function(data, e){
            console.log(ko.toJSON(data));
        },

        toggleTile: function(data, e){
            $('#abc'+data.tileid()).toggle('fast');
        },

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
