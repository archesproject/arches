define(['jquery', 'backbone'], function ($, Backbone) {
    return Backbone.View.extend({
        
        events: function(){
            return {
                'click #submitform': 'submit'  
            }
        },

        initialize: function() {
            this.form = this.$el;
            this.formdata = JSON.parse(this.form.find('#formdata').val());
            this._rawdata = JSON.parse(this.form.find('#formdata').val());
        },

        getData: function(){
            return this.formdata;
        },

        validate: function(){
            return true;
        },

        submit: function(){
            if (this.validate()){
                //this.formdata = this.getData();
                this.form.find('#formdata').val(this.getData());
                this.form.submit(); 
            }
        }

    });
});