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
        var self = this;

        params.configKeys || (params.configKeys = []);
        if (!_.contains(params.configKeys, 'options')) {
            params.configKeys.push('options');
        }

        WidgetViewModel.apply(this, [params]);

        this.multiple = false;

        this.flatOptions = ko.computed(function () {
            var options = self.options();
            var flatOptions = [];
            options.forEach(function(option) {
                var value = self.value();
                if (!Array.isArray(value)) {
                    var valueArray = [];
                    if (value) {
                        valueArray.push(value);
                    }
                    value = valueArray
                }
                option.selected = ko.computed({
                    read: function () {
                        var selected = false;
                        if (self.value()) {
                            selected = self.value().indexOf(option.id) >= 0;
                        }
                        return selected;
                    },
                    write: function (newValue) {
                        if (newValue) {
                            value.push(option.id);
                            self.value(value);
                        } else {
                            self.value(_.without(value, option.id));
                        }
                    }
                });
                gatherChildren(option, flatOptions);
            });
            return flatOptions;
        });

        var findConceptLabel = function (conceptId) {
            var label = null;
            var concept = _.find(self.flatOptions(), function (concept) {
                return concept.id === conceptId;
            });
            if (concept) {
                label = concept.text;
            }
            return label;
        };

        this.displayValue = ko.computed(function () {
            var value = self.value();
            var displayValue = null;
            if (value) {
                if (!Array.isArray(value)) {
                    value = [value];
                }
                displayValue = _.map(value, function(conceptId) {
                    return findConceptLabel(conceptId);
                }).join(', ');
            }
            return displayValue;
        });

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

    var gatherChildren = function (current, list) {
        list.push(current);
        current.children.forEach(function (child) {
            gatherChildren(child, list);
        });
        return list;
    }

    return ConceptWidgetViewModel;
});
