define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'bindings/datepicker'
], function (ko, _, WidgetViewModel, arches) {
    /**
    * registers a datepicker-widget component for use in forms
    * @function external:"ko.components".datepicker-widget
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the text input
    * @param {string} params.config.minDate - Minimum date allowed to be chosen
    * @param {string} params.config.maxDate - Maximum date allowed to be chosen
    * @param {string} params.config.viewMode - The default view to display when the picker is shown. (Accepts: 'decades','years','months','days')
    */
    return ko.components.register('datepicker-widget', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['minDate','maxDate','viewMode']
            WidgetViewModel.apply(this, [params]);
            // this.disabledTimeIntervals = ko.observable([]);
            this.placeholder = params.config().placeholder;
        },
        template: { require: 'text!widget-templates/datepicker' }
    });
});
