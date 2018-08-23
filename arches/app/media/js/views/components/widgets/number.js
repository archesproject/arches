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


    var NumberWidget = function(params) {
        params.configKeys = ['placeholder', 'width', 'min', 'max', 'step', 'precision', 'prefix', 'suffix', 'defaultValue'];

        WidgetViewModel.apply(this, [params]);

        var self = this;

        var updateVal = ko.computed(function(){
            if (self.value()){
                var val = self.value();
                if (self.precision()) {
                    val = Number(val).toFixed(self.precision());
                }
                self.value(Number(val));
            }
        }, self).extend({ throttle: 600 });

        if (ko.isObservable(this.precision)) {
            var precisionSubscription = this.precision.subscribe(function(val){
                if (self.value() && val){
                    self.value(Number(self.value()).toFixed(val));
                }
            }, self);
            self.disposables.push(precisionSubscription);
        }
        self.disposables.push(updateVal);
    };

    return ko.components.register('number-widget', {
        viewModel: NumberWidget,
        template: { require: 'text!widget-templates/number' }
    });
});
