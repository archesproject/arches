define(['jquery', 'backbone', 'bootstrap', 'dropzone'], function ($, Backbone) {
    return Backbone.View.extend({
        initialize: function(options) {
            this.$el.find('.dropzone').dropzone({
                //url: "/file/post",
                addRemoveLinks : true,
                maxFilesize: 0.5,
                dictResponseError: 'Error uploading file!'
            });
            this.$el.find('.modal').modal('show');
        }
    });
});