define([
    'knockout',
], function(ko) {
    function viewModel(params) {
        this.value = params.value;
        this.locked = params.form.locked;
    }

    ko.components.register('dataset-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/upload-dataset/dataset-step.htm'
        }
    });
});