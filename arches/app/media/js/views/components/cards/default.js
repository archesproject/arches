define([
    'knockout',
    'viewmodels/card-component'
], function(ko, CardComponentViewModel) {
    return ko.components.register('default-card', {
        viewModel: CardComponentViewModel,
        template: window['default-card-template']
    });
});
