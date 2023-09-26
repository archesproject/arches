define(['jquery', 'arches', 'backbone', 'dropzone', 'js-cookie', 'bootstrap'], function($, arches, Backbone, dropzone, Cookies) {
    return Backbone.View.extend({
        events: {
            'click button': 'close'
        },
        initialize: function(options) {
            var self = this,
                dropzoneEl = this.$el.find('.dropzone'),
                dropzoneInstance;
            // detect if dropzone is attached, and if not init
            if (!dropzoneEl.hasClass('dz-clickable')) {
                dropzoneInstance = new dropzone(dropzoneEl[0], {
                    url: arches.urls.concept.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.model.get('id')),
                    acceptedFiles: 'image/*',
                    headers: {
                        'X-CSRFToken': Cookies.get('csrftoken')
                    }
                });

                dropzoneInstance.on("addedfile", function(file) {
                    self.changed = true;
                });
            }

            this.$el.find('.modal').modal('show');
        },
        close: function() {
            var self = this,
                modal = this.$el.find('.modal');
            if (this.changed) {
                modal.on('hidden.bs.modal', function() {
                    self.trigger('dataChanged');
                });
            }
            modal.modal('hide');
        }
    });
});