define(['jquery', 'backbone', 'dropzone', 'bootstrap'], function ($, Backbone, dropzone) {
    return Backbone.View.extend({
        initialize: function(options) {
            var dropzoneEl = this.$el.find('.dropzone');
            // detect if dropzone is attached, and if not init
            if (!dropzoneEl.hasClass('dz-clickable')) {
                dropzoneEl.dropzone({
                    addRemoveLinks : true,
                    maxFilesize: 0.5,
                    dictResponseError: 'Error uploading file!'
                });
            }
            
            this.$el.find('.modal').modal('show');
        }
    });
});