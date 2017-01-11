define([
    'knockout',
    'views/search/base-filter',
    'widgets/map'
],
function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);

            this.resizeOnChange = ko.computed(function() {
                return ko.unwrap(options.resizeOnChange);
            });
        }
    });
});
