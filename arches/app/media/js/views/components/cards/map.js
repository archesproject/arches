define([
    'knockout',
    'viewmodels/card-component',
    'views/components/map'
], function(ko, CardComponentViewModel) {
    return ko.components.register('map-card', {
        viewModel: function(params) {
            this.map = ko.observable();

            CardComponentViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
});
