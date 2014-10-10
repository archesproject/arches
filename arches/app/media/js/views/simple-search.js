define(['jquery', 'backbone', 'select2'], function ($, Backbone) {
    return Backbone.View.extend({
        initialize: function() {
            this.$el.find('.arches_simple_search').select2({
                minimumResultsForSearch: 10
            });
        }
    });
});