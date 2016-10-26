define([
    'jquery',
    'knockout',
    'underscore',
    'viewmodels/domain-widget',
    'arches'
], function ($, ko, _, DomainWidgetViewModel, arches) {
    /**
    * A viewmodel used for concept widgets
    *
    * @constructor
    * @name ConceptWidgetViewModel
    *
    * @param  {string} params - a configuration object
    */
    var ConceptWidgetViewModel = function(params) {
        var self = this;

        params.configKeys || (params.configKeys = []);
        if (!_.contains(params.configKeys, 'options')) {
            params.configKeys.push('options');
        }

        DomainWidgetViewModel.apply(this, [params]);

        this.getConcepts = function (rootId) {
            var self = this;
            $.ajax({
                url: arches.urls.dropdown,
                data: {
                    conceptid: rootId
                },
                dataType: 'json'
            }).done(function(data) {
                self.options(data);
            });
        }

        this.node.config.topConcept.subscribe(function(rootId) {
            this.getConcepts(rootId);
        }, this);

        if (this.node.config.topConcept()) {
            this.getConcepts(this.node.config.topConcept());
        }
    };

    return ConceptWidgetViewModel;
});
