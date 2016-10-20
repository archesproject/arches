define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'bindings/chosen',
    'plugins/knockout-select2'
], function(ko, _, WidgetViewModel, arches) {
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
    return ko.components.register('concept-select-widget', {
        viewModel: function(params) {
            params.configKeys = ['placeholder', 'options'];
            this.selection = params.config.selection;

            WidgetViewModel.apply(this, [params]);

            this.displayValue = ko.observable();

            this.getConceptLabel = function() {
                var self = this;
                $.ajax({
                    url: arches.urls.get_pref_label,
                    data: {
                        valueid: this.value
                    },
                    datatype: 'json'
                }).done(function(label) {
                    self.displayValue(label.value);
                }).fail(function(err) {
                    console.log("error", err);
                });
            };

            if ((this.state === 'report' || this.state === 'display_value') && this.value() != null) {
                this.getConceptLabel();
            } else {
                this.displayValue(null);
            }

            this.node.config.topConcept.subscribe(function(newId) {
                var self = this;
                $.ajax({
                    url: arches.urls.dropdown,
                    data: {
                        conceptid: newId
                    },
                    dataType: 'json'
                }).done(function(data) {
                    self.options(data);
                }).fail(function(err) {
                    console.log("error", err);
                });
            }, this);
        },
        template: {
            require: 'text!widget-templates/concept-select'
        }
    });
});
