define([
    'jquery',
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches'
], function ($, ko, _, WidgetViewModel, arches) {
    /**
    * A viewmodel used for concept widgets
    *
    * @constructor
    * @name ConceptWidgetViewModel
    *
    * @param  {string} params - a configuration object
    */
    var ConceptWidgetViewModel = function(params) {
        params.configKeys || (params.configKeys = []);
        if (!_.contains(params.configKeys, 'options')) {
            params.configKeys.push('options');
        }

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

    };
    return ConceptWidgetViewModel;
});
