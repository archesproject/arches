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
            console.log('loading ' + this.name);
        },

        getFilter: function(filterName) {
            return ko.unwrap(this.filters[filterName]);
        }
    });
});
