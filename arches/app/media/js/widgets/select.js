define(['knockout', 'plugins/knockout-select2'], function (ko) {
    return ko.components.register('select-widget', {
        viewModel: function(params) {
            this.value = params.value;
            _.extend(this, _.pick(params.config, 'label', 'placeholder', 'options'));
        },
        template: { require: 'text!widgets/select.html' }
    });
});
