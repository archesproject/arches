define(['knockout', 'underscore'], function (ko, _) {
    /**
    * registers a text-widget component for use in forms
    */
    return ko.components.register('text-widget', {
        viewModel: function(params) {
            this.value = params.value;
            _.extend(this, _.pick(params.config, 'label', 'placeholder'));
        },
        template: { require: 'text!widget-templates/text' }
    });
});
