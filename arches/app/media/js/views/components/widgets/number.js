define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * registers a text-widget component for use in forms
    * @function external:"ko.components".text-widget
    * @param {object} params
    * @param {number} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    */
    return ko.components.register('number-widget', {
        viewModel: function(params) {
            params.configKeys = ['placeholder', 'width', 'min', 'max'];

            WidgetViewModel.apply(this, [params]);
            var self = this;
            if (ko.isObservable(this.value)) {
                this.value.subscribe(function(val){
                    if (self.value()){
                        self.value(Number(val))
                    }
                }, self);
            };
        },
        template: { require: 'text!widget-templates/number' }
    });
});
