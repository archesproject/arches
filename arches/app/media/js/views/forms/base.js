define(['jquery', 'backbone', 'knockout'], function ($, Backbone, ko) {
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
            this.formdata = JSON.parse(this.form.find('#formdata').val());
            this._rawdata = JSON.parse(this.form.find('#formdata').val());

            this.viewModel = {};

            $.each(this.formdata, function( key, value ) {
                self.viewModel[key] = ko.observableArray(value);
            });
        },

        getData: function(){
            return ko.toJSON(this.viewModel);
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