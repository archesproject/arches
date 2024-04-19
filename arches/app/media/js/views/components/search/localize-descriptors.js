define([
    'jquery',
    'knockout',
    'arches',
], function($, ko, arches) {
    const componentName = 'localize-descriptors';
    const viewModel = BaseFilter.extend({
        initialize: function(options) {
            options.name = 'Localize Result Descriptors';
            BaseFilter.prototype.initialize.call(this, options);
            this.filter = true;
            this.filters[componentName](this);
        } 
    });

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: '',
    });
});
