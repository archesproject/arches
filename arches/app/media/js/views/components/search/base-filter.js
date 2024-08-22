define([
    'jquery',
    'backbone',
    'knockout'
], function($, Backbone, ko) {
    return Backbone.View.extend({
        constructor: function() {
            this.name = 'Base Filter';
            // the various filters managed by this widget
            this.filter = {};
            // Call the original constructor
            Backbone.View.apply(this, arguments);
        },

        initialize: function(options) {
            $.extend(this, options);
        },
    });
});
