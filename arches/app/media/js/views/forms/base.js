define(['jquery', 'backbone'], function ($, Backbone) {
    return Backbone.View.extend({
        events: {
            'click #submitform': 'submit'
        },

        initialize: function() {
            this.form = this.$el;
            this.formdata = JSON.parse(this.form.find('#formdata').val());
        },

        submit: function(){
            this.form.submit();
        }
    });
});