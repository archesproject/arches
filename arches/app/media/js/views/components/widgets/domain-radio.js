import ko from 'knockout';
import DomainWidgetViewModel from 'viewmodels/domain-widget';
import radioTemplate from 'templates/views/components/widgets/radio.htm';
import 'bindings/key-events-click';


/**
 * registers a select-widget component for use in forms
 * @function external:"ko.components".select-widget
 * @param {object} params
 * @param {boolean} params.value - the value being managed
 * @param {object} params.config -
 * @param {string} params.config.label - label to use alongside the select input
 * @param {string} params.config.placeholder - default text to show in the select input
 * @param {string} params.config.options -
 */

const viewModel = function(params) {
        
    params.configKeys = ['defaultValue'];
    DomainWidgetViewModel.apply(this, [params]);
};

export default ko.components.register('domain-radio-widget', {
    viewModel: viewModel,
    template: radioTemplate,
});
