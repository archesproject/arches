define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * registers a text-widget component for use in forms
    * @function external:"ko.components".text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    */
    return ko.components.register('wkt-point-widget', {
        viewModel: function(params) {
            params.configKeys = ['x_placeholder','y_placeholder','x_value', 'y_value', 'width'];
            WidgetViewModel.apply(this, [params]);
            this.value = ko.computed(function() {
                return this.x_value() + " " + this.y_value();
                }, this);
        },
        template: { require: 'text!templates/wkt-point.htm' }
    });
});
