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
    return ko.components.register('text-widget', {
        viewModel: function(params) {
            params.configKeys = ['placeholder', 'width', 'maxLength', 'defaultValue'];
            WidgetViewModel.apply(this, [params]);

            var self = this;
            var defaultValue = ko.unwrap(this.defaultValue)

            if (this.tile && this.tile.tileid() == "" && defaultValue != null && defaultValue != "") {
                this.value(defaultValue);
            }

            if (!self.form) {
                self.value.subscribe(function(){
                    self.defaultValue(self.value())
                })
                self.defaultValue.subscribe(function(){
                    self.value(self.defaultValue())
                })
            };
        },
        template: { require: 'text!widget-templates/text' }
    });
});
