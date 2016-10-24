define([
    'knockout',
    'viewmodels/concept-widget',
    'plugins/knockout-select2'
], function(ko, ConceptWidgetViewModel) {
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
    return ko.components.register('concept-radio-widget', {
        viewModel: function(params) {
            var self = this;

            ConceptWidgetViewModel.apply(this, [params]);

            var gatherChildren = function (current, list) {
                list.push(current);
                current.children.forEach(function (child) {
                    gatherChildren(child, list);
                });
                return list;
            }

            this.radioOptions = ko.computed(function () {
                var options = self.options();
                var radioOptions = [];
                options.forEach(function(option) {
                    gatherChildren(option, radioOptions);
                });
                return radioOptions;
            });
        },
        template: {
            require: 'text!widget-templates/concept-radio'
        }
    });
});
