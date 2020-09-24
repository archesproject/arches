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
            this.requiredFilters = [];
            // Call the original constructor
            Backbone.View.apply(this, arguments);
        },

        initialize: function(options) {
            $.extend(this, options);
            this.requiredFiltersLoaded = ko.computed(function() {
                var self = this;
                var res = this.requiredFilters.every(function(f){return self.getFilter(f) !== null;});
                return res;
            }, this);
        },
    

        getFilter: function(filterName) {
            return ko.unwrap(this.filters[filterName]);
        }
    });
});
