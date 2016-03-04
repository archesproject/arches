define(['jquery', 
    'backbone', 
    'knockout',
    'knockout-mapping', 
    'underscore',
    'models/config'
], function ($, Backbone, ko, koMapping, _, ConfigModel) {
    return Backbone.View.extend({

        initialize: function() {
            var self = this;
            this.form = this.$el;

            // parse then restringify JSON data to ensure whitespace is identical
            this._rawdata = ko.toJSON(JSON.parse(this.form.find('#tiledata').val()));
            this.cardgroups = koMapping.fromJS(JSON.parse(this._rawdata));
            
            this.tiles = koMapping.fromJS(JSON.parse(this._rawdata));

        },

        saveTile: function(data, e){
            console.log(ko.toJS(data));
            var cardid = data.cardid();
            var model = new ConfigModel(ko.toJS(data));
            model.save(function(request, status, model){
                if(request.status === 200){
                    if(!(cardid in this)){
                        this[cardid].tiles = koMapping.fromJS([]);
                    }
                    this[cardid].tiles.unshift(koMapping.fromJS(request.responseJSON));
                }else{
                    // inform the user
                }
            }, this);
        },

        updateTile: function(data, e){
            console.log(ko.toJS(data));
            var model = new ConfigModel(ko.toJS(data));
            model.save(function(request, status, model){
                if(request.status === 200){
                    // inform the user???
                }else{
                    // inform the user
                }
            }, this);
        },

        deleteTile: function(data, e){
            console.log(ko.toJSON(data));
            var cardid = data.cardid();
            var model = new ConfigModel(ko.toJS(data));
            model.delete(function(request, status, model){
                if(request.status === 200){
                    this[cardid].tiles.remove(data)
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