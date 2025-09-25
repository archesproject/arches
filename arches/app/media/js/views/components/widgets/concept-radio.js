import ko from 'knockout';
import ConceptWidgetViewModel from 'viewmodels/concept-widget';
import conceptRadioTemplate from 'templates/views/components/widgets/radio.htm';
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
        
    ConceptWidgetViewModel.apply(this, [params]);
};

export default ko.components.register('concept-radio-widget', {
    viewModel: viewModel,
    template: conceptRadioTemplate,
});
