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
            this.requiredFilters = this.getRequiredFilters(this.componentName);
            this.requiredFiltersLoaded = ko.computed(function() {
                let res = true;
                Object.entries(this.filters).forEach(function([componentName, filter]) {
                    res = res && filter !== null;
                });
                return res;
            }, this);
        },
    

        getFilter: function(filterName) {
            return ko.unwrap(this.filters[filterName]);
        }
    });
});
