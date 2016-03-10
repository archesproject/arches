define([
    'jquery',
    'backbone',
    'knockout',
    'knockout-mapping',
    'underscore'
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
            this.blanks = JSON.parse(this.form.find('#blanks').val());

            this.tiles = koMapping.fromJS(JSON.parse(this._rawdata));

            console.log(JSON.parse(this._rawdata));

        },

        saveTile: function(tilegroup, tile, e){
            console.log(ko.toJS(tile));
            var nodegroupid = tile.nodegroupid();
            var model = new this.TileModel(ko.toJS(tile));
            model.save(function(request, status, model){
                if(request.status === 200){
                    if(!(nodegroupid in tilegroup)){
                        tilegroup[nodegroupid] = koMapping.fromJS([]);
                    }
                    tilegroup[nodegroupid].unshift(koMapping.fromJS(request.responseJSON));
                }else{
                    // inform the user
                }
            }, this);
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
            var nodegroupid = tile.nodegroupid();
            var model = new this.TileModel(ko.toJS(tile));
            model.delete(function(request, status, model){
                if(request.status === 200){
                    tilegroup[nodegroupid].remove(tile)
                }else{
                    // inform the user
                }
            }, this);
        },

        cancelEdit: function(data, e){
            console.log(ko.toJSON(data));
        },

        expandTile: function(data, e){
            console.log(ko.toJSON(data));
            if(!self.collapsing){
                $(e.currentTarget).find('.effect').show('slow');
            }else{
                self.collapsing = false;
            }
        },

        collapseTile: function(data, e){
            console.log(ko.toJSON(data));
            $(e.currentTarget.parentElement).hide('slow');
            self.collapsing = true;
        }
    });
});
