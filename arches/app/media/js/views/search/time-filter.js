define([
    'views/search/base-filter',
    'bindings/chosen'
],
function(BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
        },

        appendFilters: function(queryStringObject) {
            return false;
        },

        restoreState: function(filter) {
            return;
        },

        clear: function() {
            return;
        }
    });
});
