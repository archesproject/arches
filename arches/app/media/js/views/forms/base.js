define(['jquery', 'backbone', 'knockout', 'plugins/knockout-select2'], function ($, Backbone, ko) {
    return Backbone.View.extend({
        
        events: function(){
            return {
                'click #submitform': 'submit'  
            }
        },

        constructor: function (options) {
            Backbone.View.apply(this, arguments);

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
        },

        isDirty: function () {
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