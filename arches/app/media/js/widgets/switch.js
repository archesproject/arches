define(['knockout', 'underscore'], function (ko, _) {
    return ko.components.register('switch-widget', {
        viewModel: function(params) {
            this.value = params.value;
            _.extend(this, _.pick(params.config, 'label', 'placeholder'));
        },
        template: { require: 'text!widgets/switch.html' }
    });
});
