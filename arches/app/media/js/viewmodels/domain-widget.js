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

        this.testValArray = ko.isObservable(params.value) && 'push' in params.value ? params.value : params.value = ko.observableArray();
        this.testValArray.subscribe(function(item){
            console.log(item);
        })

        var flattenOptions = function(opt, allOpts) {
            allOpts.push(opt);
            if (opt.children) {
                opt.children.forEach(function(child) {
                    flattenOptions(child, allOpts);
                });
            }
            if (typeof opt.selected !== 'function') {
                opt.selected = ko.computed({
                    read: function() {
                        var selected = false;
                        var val = self.value();
                        if (val && val.indexOf) {
                            selected = val.indexOf(opt.id) >= 0;
                        }
                        return selected;
                    },
                    write: function(selected) {
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
                    }
                });
            }
            return allOpts;
        };

        this.flatOptions = ko.computed(function() {
            var options = self.options();
            var flatOptions = [];
            options.forEach(function(option) {
                flattenOptions(option, flatOptions);
            });
            return flatOptions;
        });

        this.toggleCheckedState = function(item){
            console.log(item)
            if(params.value().indexOf(item.id) === -1){
                params.value.push(item.id);
            }else{
                params.value.remove(item.id);
            }
        }

        this.optionsArrray = ko.observableArray(this.flatOptions());
        console.log(this.flatOptions());

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
