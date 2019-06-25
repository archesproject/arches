define([
    'knockout',
    'viewmodels/card-component',
    'views/components/map'
], function(ko, CardComponentViewModel, MapComponentViewModel) {
    return ko.components.register('map-card', {
        viewModel: function(params) {
            CardComponentViewModel.apply(this, [params]);
            MapComponentViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
});
