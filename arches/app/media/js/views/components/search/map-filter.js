define([
    'jquery',
    'underscore',
    'arches',
    'knockout',
    'views/components/map'
], function($, _, arches, ko, MapComponentViewModel) {
    var componentName = 'map-filter';
    var viewModel = function(params) {
        var self = this;
        MapComponentViewModel.apply(this, [params]);
    };
    ko.components.register(componentName, {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/search/map-filter.htm'
        }
    });
    return viewModel;
});
