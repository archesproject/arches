define([
    'knockout',
    'viewmodels/card-component'
], function(ko, CardComponentViewModel) {
    return ko.components.register('default-card', {
        viewModel: CardComponentViewModel,
        template: {
            require: 'text!templates/views/components/cards/default.htm'
        }
    });
});
