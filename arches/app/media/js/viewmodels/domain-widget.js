define([
    'knockout',
    'underscore',
    'viewmodels/widget'
], function(ko, _, WidgetViewModel) {
    /**
     * A viewmodel used for domain widgets
     *
     * @constructor
     * @name DomainWidgetViewModel
     *
     * @param  {string} params - a configuration object
     */
    var DomainWidgetViewModel = function(params) {
        var self = this;

        WidgetViewModel.apply(this, [params]);

        if (this.node.config.options) {
            this.options = this.node.config.options;
            this.options().forEach(function(option) {
                if (!ko.isObservable(option.text)) {
                    option.text = ko.observable(option.text);
                }
            })
            this.node.configKeys.valueHasMutated();
        }

        this.flatOptions = ko.computed(function() {
            var options = self.options();
            var flatOptions = [];
            var value = self.value();
            if (!Array.isArray(value)) {
                var valueArray = [];
                if (value) {
                    valueArray.push(value);
                }
                value = valueArray
            }
            var setupOption = function(option) {
                option.selected = ko.computed({
                    read: function() {
                        var selected = false;
                        var value = self.value();
                        if (value && value.indexOf) {
                            selected = value.indexOf(option.id) >= 0;
                        }
                        return selected;
                    },
                    write: function(selected) {
                        if (self.multiple) {
                            var value = self.value();
                            self.value(
                                selected ?
                                _.union(value, [option.id]) :
                                _.without(value, option.id)
                            );
                        } else if (selected) {
                            self.value(option.id);
                        }
                    }
                });
            }
            options.forEach(function(option) {
                setupOption(option);
                gatherChildren(option, flatOptions, setupOption);
            });
            return flatOptions;
        });

        this.multiple = false;

        this.displayValue = ko.computed(function() {
            var value = self.value();
            var options = ko.unwrap(self.flatOptions);
            var displayValue = null;
            if (value) {
                if (!Array.isArray(value)) {
                    value = [value];
                }
                displayValue = _.map(value, function(id) {
                    var text = null;
                    var option = _.find(options, function(option) {
                        return option.id === id;
                    });
                    if (option) {
                        text = ko.unwrap(option.text);
                    }
                    return text;
                })
                displayValue = _.without(displayValue, null).join(', ');
            }
            return displayValue;
        });
    };

    var gatherChildren = function(current, list, callback) {
        list.push(current);
        if (current.children) {
            current.children.forEach(function(child) {
                gatherChildren(child, list, callback);
            });
        }
        callback(current);
        return list;
    };

    return DomainWidgetViewModel;
});
