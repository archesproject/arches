define([
    'jquery',
    'knockout',
    'arches',
], function($, ko, arches) {
    const componentName = 'core-search';
    const viewModel = BaseFilter.extend({
        initialize: function(options) {
            options.name = 'Core Search';
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
