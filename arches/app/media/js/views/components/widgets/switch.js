define(['knockout', 'underscore', 'viewmodels/widget'], function(ko, _, WidgetViewModel) {
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

    var SwitchWidget = function(params) {
        params.configKeys = ['subtitle', 'defaultValue'];
        WidgetViewModel.apply(this, [params]);
        this.on = this.config().on || true;
        this.off = this.config().off || false;
        this.null = this.config().null || null;
        this.setvalue = this.config().setvalue || function(self, evt){
            if (ko.unwrap(self.disabled) === false) {
                if(self.value() === self.on){
                    self.value(self.null);
                }else if (self.value() === self.null) {
                    self.value(self.off);
                }else if (self.value() === self.off) {
                    self.value(self.on);
                }
            }
        };
        this.getvalue = this.config().getvalue || ko.computed(function(){
            var result = null;
            if (this.value() === this.on) {
                result = true;
            } else if (this.value() === false) {
                result = false;
            }
            return result;
        }, this);

        this.setdefault = this.config().setdefault || function(self){
            if(self.defaultValue() === self.on){
                self.defaultValue(self.null);
            }else if(self.defaultValue() === self.null){
                self.defaultValue(self.off);
            }else if(self.defaultValue() === self.off){
                self.defaultValue(self.on);
            }
        };

        this.getdefault = this.config().getdefault || ko.computed(function(){
            var result = null;
            if (this.defaultValue() === this.on) {
                result = true;
            } else if (this.defaultValue() === false) {
                result = false;
            }
            return result;
        }, this);

        var defaultValue = ko.unwrap(this.defaultValue);
        if (this.value() === null && this.defaultValue() !== null) {
            this.value(this.defaultValue());
        }
        if (this.tile && this.tile.tileid == "" && defaultValue != null && defaultValue != "") {
            this.value(defaultValue);
        }
        this.disposables.push(this.getvalue);
        this.disposables.push(this.setdefault);
        this.disposables.push(this.getdefault);
    };

    return ko.components.register('switch-widget', {
        viewModel: SwitchWidget,
        template: { require: 'text!widget-templates/switch' }
    });
});
