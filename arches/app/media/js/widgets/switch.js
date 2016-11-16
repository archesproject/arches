define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * knockout components namespace used in arches
    * @external "ko.components"
    * @see http://knockoutjs.com/documentation/component-binding.html
    */

    /**
    * registers a switch-widget component for use in forms
    * @function external:"ko.components".switch-widget
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the select input
    * @param {string} params.config.subtitle - subtitle to use alongside the select input
    * @param {string|true} [params.config.on=true] - the value to use for the "on" state of the switch
    * @param {string|false} [params.config.off=false] - the value to use for the "off" state of the switch
    */
    return ko.components.register('switch-widget', {
        viewModel: function(params) {
            params.configKeys = ['subtitle'];
            WidgetViewModel.apply(this, [params]);
            this.on = this.config().on || true;
            this.off = this.config().off || false;
            this.setvalue = this.config().setvalue || function(self, evt){
                if(self.value() === self.on){
                    self.value(self.off);
                }else{
                    self.value(self.on);
                }
            }
            this.getvalue = this.config().getvalue || ko.computed(function(){
                return this.value() === this.on;
            }, this);
        },
        template: { require: 'text!widget-templates/switch' }
    });
});
