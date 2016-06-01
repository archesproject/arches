define(['knockout'], function (ko) {
    return ko.components.register('text-widget', {
        viewModel: function(params) {
            this.value = params.value;
            _.extend(this, _.pick(params.config, 'label', 'placeholder'));
        },
        template: { require: 'text!widgets/text.html' }
    });
});
