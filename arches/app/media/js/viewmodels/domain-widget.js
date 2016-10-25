define([
    'knockout',
    'underscore',
    'viewmodels/widget'
], function (ko, _, WidgetViewModel) {
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
        }

        this.flatOptions = ko.computed(function () {
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
            options.forEach(function(option) {
                option.selected = ko.computed({
                    read: function () {
                        var selected = false;
                        if (self.value()) {
                            selected = self.value().indexOf(option.id) >= 0;
                        }
                        return selected;
                    },
                    write: function (newValue) {
                        if (self.multiple) {
                            if (newValue) {
                                value.push(option.id);
                                self.value(value);
                            } else {
                                self.value(_.without(value, option.id));
                            }
                        } else if (newValue) {
                            self.value(option.id);
                        }
                    }
                });
                gatherChildren(option, flatOptions);
            });
            return flatOptions;
        });

        this.multiple = false;

        this.findText = function (id) {
            var text = null;
            var option = _.find(ko.unwrap(self.options), function (option) {
                return option.id === id;
            });
            if (option) {
                text = option.text;
            }
            return text;
        };

        this.displayValue = ko.computed(function () {
            var value = self.value();
            var displayValue = null;
            if (value) {
                if (!Array.isArray(value)) {
                    value = [value];
                }
                displayValue = _.map(value, function(id) {
                    return self.findText(id);
                }).join(', ');
            }
            return displayValue;
        });
    };

    var gatherChildren = function (current, list) {
        list.push(current);
        if (current.children) {
            current.children.forEach(function (child) {
                gatherChildren(child, list);
            });
        }
        return list;
    };

    return DomainWidgetViewModel;
});
