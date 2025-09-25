import ko from 'knockout';
import _ from 'underscore';
import WidgetViewModel from 'viewmodels/widget';
import radioBooleanWidgetTemplate from 'templates/views/components/widgets/radio-boolean.htm';
import 'bindings/key-events-click';


/**
* knockout components namespace used in arches
* @external "ko.components"
* @see http://knockoutjs.com/documentation/component-binding.html
*/

/**
* registers a radio-boolean-widget component for use in forms
* @function external:"ko.components".radio-boolean-widget
* @param {object} params
* @param {boolean} params.value - the value being managed
* @param {boolean} params.defaultValue - automatically assigned to value when the widget appears in a form
* @param {object} params.config -
* @param {string} params.config.label - label to use alongside the select input
* @param {string} params.config.trueValue - label alongside the true boolean button
* @param {string} params.config.falseValue - label alongside the false boolean button
*/

const viewModel = function(params) {
    params.configKeys = ['trueLabel', 'falseLabel', 'defaultValue'];
        
    WidgetViewModel.apply(this, [params]);
    var self = this;
    this.setValue = function(val) {
        if (ko.unwrap(self.disabled) === false) {
            if (val === self.value()) {
                self.value(null);
            } else {
                self.value(val);
            }
        }
    };

    this.displayValue = ko.computed(function() {
        if (this.value()===true) {
            return this.node.config.trueLabel;
        }
        else if (this.value()===false) {
            return this.node.config.falseLabel;
        }
    }, self);

    this.setDefaultValue = function(val) {
        if (val === self.defaultValue()) {
            self.defaultValue(null);
        } else {
            self.defaultValue(val);
        }
    };

    var defaultValue = ko.unwrap(this.defaultValue);
    if (self.value() === null && self.defaultValue() !== null) {
        self.value(self.defaultValue());
    }
    if (this.tile && ko.unwrap(this.tile.tileid) == "" && defaultValue != null && defaultValue != "") {
        this.value(defaultValue);
    }
};

export default ko.components.register('radio-boolean-widget', {
    viewModel: viewModel,
    template: radioBooleanWidgetTemplate,
});
