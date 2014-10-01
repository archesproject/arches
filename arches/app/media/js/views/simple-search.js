define(['jquery', 'backbone', 'select2'], function ($, Backbone) {
    return Backbone.View.extend({
        id: 'SimpleSearch',
        initialize: function() {
            $("#" + this.id).select2({
                minimumResultsForSearch: 10
            });
        }
    });
});