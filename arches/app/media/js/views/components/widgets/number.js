define(['knockout', 'underscore', 'viewmodels/widget', 'bindings/formattedNumber'], function (ko, _, WidgetViewModel) {
    /**
    * registers a text-widget component for use in forms
    * @function external:"ko.components".text-widget
    * @param {object} params
    * @param {number} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    * @param {string} params.config().uneditable - disables widget
    */


    var NumberWidget = function(params) {
        params.configKeys = ['placeholder', 'width', 'min', 'max', 'step', 'precision', 'prefix', 'suffix', 'defaultValue', 'format', 'uneditable'];

        WidgetViewModel.apply(this, [params]);

        var self = this;

        this.updateVal = ko.computed(function(){
            if (self.value() !== null && self.value() !== undefined) { //allow a value of 0 to pass
                var val = self.value();
                if (typeof self.min() === 'number') {
                    val = Number(val) < Number(self.min()) ? Number(self.min()) : Number(val);
                }

                if (typeof self.max() === 'number') {
                    val = Number(val) > Number(self.max()) ? Number(self.max()) : Number(val);
                }

                if (self.precision()) {
                    val = Number(val).toFixed(self.precision());
                }

            }
            return val || self.value();
        }, self).extend({throttle: 600});

        this.value(Number(this.updateVal()));

        this.displayValue = ko.pureComputed(function() {
            if (self.value() !== null && self.value() !== undefined) {
                return self.value().toString();
            }
        }, self);

        if (ko.isObservable(this.precision)) {
            var precisionSubscription = this.precision.subscribe(function(val){
                if (self.value() && val){
                    self.value(Number(self.value()).toFixed(val));
                }
            }, self);
            self.disposables.push(precisionSubscription);
        }
        self.disposables.push(this.updateVal);
    };

    return ko.components.register('number-widget', {
        viewModel: NumberWidget,
        template: { require: 'text!widget-templates/number' }
    });
});
