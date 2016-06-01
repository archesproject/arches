define(['knockout', 'bindings/datepicker'], function (ko) {
    return ko.components.register('datepicker-widget', {
        viewModel: function(params) {
            this.value = params.value;
            _.extend(this, _.pick(params.config, 'label', 'placeholder'));
        },
        template: { require: 'text!widgets/datepicker.html' }
    });
});
