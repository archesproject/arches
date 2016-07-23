define(['knockout', 'underscore'], function (ko, _) {
    /**
    * registers a switch-widget component for use in forms
    */
    return ko.components.register('switch-widget', {
        viewModel: function(params) {
            this.value = params.value;
            _.extend(this, _.pick(params.config, 'label', 'subtitle'));
        },
        template: { require: 'text!widget-templates/switch' }
    });
});
