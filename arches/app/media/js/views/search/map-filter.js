define([
    'views/search/base-filter',
    'widgets/map'
],
function(BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
        }
    });
});
