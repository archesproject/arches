define([
    'jquery',
    'backbone'
], function($, Backbone) {
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
            return this.filters[filterName]();
        }
    });
});
