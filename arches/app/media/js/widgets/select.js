define(['knockout', 'plugins/knockout-select2'], function (ko) {
    return ko.components.register('select-widget', {
        viewModel: function(params) {
            this.selectedValue = params.value;
            this.label = params.config.label;
            this.placeholder = params.config.placeholder;
            this.options = params.config.options;
        },
        template: { require: 'text!widgets/select.html' }
    });
});
