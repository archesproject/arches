define([
    'knockout'
], function(ko) {
    return ko.components.register('new-tile-step', {
        viewModel: function(params) {
            console.log(params);
            params.complete(true);
        },
        template: {
            require: 'text!templates/views/components/workflows/new-tile-step.htm'
        }
    });
});
