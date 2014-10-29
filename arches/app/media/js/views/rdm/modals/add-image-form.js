define(['jquery', 'backbone', 'dropzone', 'arches', 'bootstrap'], function ($, Backbone, dropzone, arches) {
    return Backbone.View.extend({
        initialize: function(options) {
            var dropzoneEl = this.$el.find('.dropzone');
            // detect if dropzone is attached, and if not init
            if (!dropzoneEl.hasClass('dz-clickable')) {
                dropzoneEl.dropzone({
                    url: arches.urls.concept_image.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.model.get('id')),
                    addRemoveLinks : true,
                    maxFilesize: 0.5,
                    dictResponseError: 'Error uploading file!'
                });
            }

            this.$el.find('.modal').modal('show');
        }
    });
});