define([
    'knockout',
    'viewmodels/card-component',
    'templates/views/components/cards/default.htm',
], function(ko, CardComponentViewModel, defaultCardTemplate) {
    return ko.components.register('default-card', {
        viewModel: CardComponentViewModel,
        template: defaultCardTemplate,
    });
});