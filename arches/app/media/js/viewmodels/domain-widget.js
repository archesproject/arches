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
            });
            // force the node config to refresh (so it detects text observables)
            this.node.configKeys.valueHasMutated();
        }

        var flattenOptions = function(opt, allOpts) {
            if (opt['id'] !== undefined) {
                allOpts.push(opt);
            }
            if (opt.children) {
                opt.children.forEach(function(child) {
                    flattenOptions(child, allOpts);
                });
            }
            return allOpts;
        };

        this.toggleOptionSelection = function (opt) {
            var selected = !self.isOptionSelected(opt);
            self.setOptionSelection(opt, selected);
        };

        this.setOptionSelection = function (opt, selected) {
            if (self.multiple) {
                var val = self.value();
                self.value(
                    selected ?
                    _.union([opt.id], val) :
                    _.without(val ? val : [], opt.id)
                );
            } else if (selected) {
                self.value(opt.id);
            }
        };

        this.isOptionSelected = function (opt) {
            var selected = false;
            var val = self.value();
            if (val && val.indexOf) {
                selected = val.indexOf(opt.id) >= 0;
            }
            return selected;
        };

        this.flatOptions = ko.computed(function() {
            var options = self.options();
            var flatOptions = [];
            options.forEach(function(option) {
                flattenOptions(option, flatOptions);
            });
            return flatOptions;
        });

        this.multiple = false;

        this.displayValue = ko.computed(function() {
            var val = self.value();
            var opts = ko.unwrap(self.flatOptions);
            var displayVal = null;
            if (val) {
                Array.isArray(val) || (val = [val]);
                displayVal = _.without(
                    _.map(val, function(id) {
                        var opt = _.find(opts, function(opt) {
                            return opt.id === id;
                        });
                        return opt ? ko.unwrap(opt.text) : null;
                    }),
                    null
                ).join(', ');
            }
            return displayVal;
        });
    };


    return DomainWidgetViewModel;
});
