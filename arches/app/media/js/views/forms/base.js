define(['jquery', 'backbone', 'knockout', 'underscore', 'plugins/knockout-select2', 'plugins/knockout-summernote'], function ($, Backbone, ko, _) {
    return Backbone.View.extend({
        
        events: function(){
            return {
                'click .save-edits': 'submit',
                'click .cancel-edits': 'cancel'
            }
        },

        constructor: function (options) {
            var self = this;
            this.branchLists = [];

            ko.observableArray.fn.get = function(entitytypeid, key) {
                var allItems = this();
                var ret = '';
                _.filter(allItems, function(node){
                    if ('entitytypeid' in node && entitytypeid.search(node.entitytypeid()) > -1){
                        ret = node[key]();
                        return true;
                    }
                }, this);
                return ret
            }

            Backbone.View.apply(this, arguments);
            
            return this;
        },

        initialize: function() {
            var self = this;
            this.form = this.$el;
            // parse then restringify JSON data to ensure whitespace is identical
            this._rawdata = ko.toJSON(JSON.parse(this.form.find('#formdata').val()));
            this.data = JSON.parse(this._rawdata);

            // $('input,select').change(function() {
            //     var isDirty = self.isDirty();
            //     self.trigger('change', isDirty);
            // });

            this.on('change', function(eventtype, item){
                $('.save-edits').removeClass('disabled');
                $('.cancel-edits').removeClass('disabled');                    
            });

            this.$el.find('.form-load-mask').hide();
        },

        addBranchList: function(branchList){
            var self = this;
            this.branchLists.push(branchList);
            this.listenTo(branchList, 'change', function(eventtype, item){
                self.trigger('change', eventtype, item);                 
            });
            return branchList;
        },

        isDirty: function () {
            // var viewModel = JSON.parse(ko.toJSON(this.viewModel));
            // for(branch in ko.toJS(this.viewModel)){
            //     if(branch !== 'domains' && branch !== 'defaults' && branch !== 'editing'){
            //         for(index in viewModel[branch]){
            //             for(item in viewModel[branch][index]){
            //                 if(item.indexOf('entityid') > 0){
            //                     if(viewModel[branch][index][item] === ''){
            //                         return true;
            //                         break;
            //                     }
            //                 }                            
            //             }
            //         }                    
            //     }
            // }
            return this.getData(true) !== this._rawdata;
        },

        getData: function(includeDomains){
            var data = {};
            _.each(this.branchLists, function(branchList){
                data[branchList.dataKey] = branchList.getData();
            }, this);  
            return ko.toJSON(data);
        },

        validate: function(){
            var isValid = true
            _.each(this.branchLists, function(branchList){
                isValid = isValid && branchList.validate();
            }, this); 
            return isValid;
        },

        submit: function(evt){
            evt.preventDefault();
            
            if (this.validate()){
                this.form.find('#formdata').val(this.getData());
                this.form.submit(); 
            }
        },

        cancel: function(evt){
            _.each(this.branchLists, function(branchList){
                branchList.undoAllEdits();
            }, this);  
        }
    });
});