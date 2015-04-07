define(['jquery', 'backbone', 'arches'], function ($, Backbone, arches) {
    return Backbone.View.extend({
        events: {
            'click .delete-resource-btn': 'deleteResource'
        },

        deleteResource: function() {
            $.ajax({
                method: 'DELETE',
                url: '',
                success: function() {
                    location.href = arches.urls.home;
                }
            });
        }
    });
});
