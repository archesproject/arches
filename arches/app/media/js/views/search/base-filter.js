define(['jquery', 'backbone', 'knockout'], function($, Backbone, ko) {
    return Backbone.View.extend({
        filter: {
            // the various filters managed by this search filter widget
        },

        initialize: function(options) {
            $.extend(this, options);

            this.changed = ko.pureComputed(function(){
                var ret = ko.toJSON(this.filter);
                return ret;
            }, this);
        },


        hasFilters: function() {
            // returns a boolean true if this filter is currently active, else false
        },

        appendFilters: function(queryStringObject) {
            // append your filters onto this object which ultimately is used in the URL

            return queryStringObject;
        },

        restoreState: function(filter) {
            // a function to drive the state of the ui based on
            // the filter object passed into the function
            // the filter objects should take the same form as this.query.filter
        },

        clear: function() {
            // a function that clears the filter and restores
            // the ui to a clean and unfiltered state
        }
    });
});
