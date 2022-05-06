define(['knockout', 'viewmodels/widget', 'utils/create-async-component'], function(ko, WidgetViewModel, createAsyncComponent) {
    /**
    * knockout components namespace used in arches
    * @external "ko.components"
    * @see http://knockoutjs.com/documentation/component-binding.html
    */

    /**
    * registers a switch-widget component for use in forms
    * @function external:"ko.components".simple-switch
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the select input
    * @param {string} params.config.subtitle - subtitle to use alongside the select input
    * @param {string|true} [params.config.on=true] - the value to use for the "on" state of the switch
    * @param {string|false} [params.config.off=false] - the value to use for the "off" state of the switch
    */

    return createAsyncComponent(
        'views/components/simple-switch', 
        function(params) {
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
            };
            this.getvalue = this.config().getvalue || ko.computed(function(){
                return this.value() === this.on;
            }, this);
        }, 
        'templates/views/components/simple-switch.htm'
    );
});
