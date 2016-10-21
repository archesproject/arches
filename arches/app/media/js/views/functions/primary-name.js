define(['knockout', 'viewmodels/function'], function (ko, FunctionViewModel) {
    return ko.components.register('primary-name', {
        viewModel: function(params) {
            
        },
        template: {
            require: 'text!function-templates/primary-name'
        }
    });
})