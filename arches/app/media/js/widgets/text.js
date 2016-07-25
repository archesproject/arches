define(['knockout', 'underscore'], function (ko, _) {
    /**
    * registers a text-widget component for use in forms
    */
    return ko.components.register('text-widget', {
        viewModel: function(params) {
            this.value = params.value;
            this.label = params.label;
            _.extend(this, _.pick(params.config, 'placeholder'));
        },
        template: { require: 'text!widget-templates/text' }
    });
});
