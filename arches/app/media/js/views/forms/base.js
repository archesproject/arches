define(['jquery', 'backbone', 'knockout', 'underscore', 'plugins/knockout-select2'], function ($, Backbone, ko, _) {
    return Backbone.View.extend({
        
        events: function(){
            return {
                'click #saveedits': 'submit'  
            }
        },

        constructor: function (options) {
            var self = this;

            Backbone.View.apply(this, arguments);
            
            _.each(this.branchLists, function(branchList) {
                self.listenTo(branchList, 'change', function(eventtype, item){
                    self.trigger('change', eventtype, item);                 
                });
            });

            ko.applyBindings(this.viewModel, this.el);
            return this;
        },

        initialize: function() {
            var self = this;
            this.form = this.$el;
            // parse then restringify JSON data to ensure whitespace is identical
            this._rawdata = ko.toJSON(JSON.parse(this.form.find('#formdata').val()));
            this.viewModel = JSON.parse(this._rawdata);
            this.viewModel.editing = {};
            this.viewModel.formatDomainValue = function (item) {
                return item.value;
            };

            this.viewModel.selectDomainValue = function (item) {
                if (this.labelValue) {
                    this.labelValue(item.value);
                }
                return self.viewModel.formatDomainValue(item);
            };

            $('input,select').change(function() {
                var isDirty = self.isDirty();
                self.trigger('change', isDirty);
            });

            this.on('change', function(eventtype, item){
                console.log(eventtype);
                console.log(item);
                $('#saveedits').removeClass('disabled');
                $('#canceledits').removeClass('disabled');                    
            });

            this.branchLists = [];
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
            var data = ko.toJS(this.viewModel)
            if (!includeDomains) {
                delete data.domains;
            }
            delete data.editing;
            return ko.toJSON(data);
        },

        validate: function(){
            return true;
        },

        submit: function(){
            if (this.validate()){
                this.form.find('#formdata').val(this.getData());
                this.form.submit(); 
            }
        }
    });
});