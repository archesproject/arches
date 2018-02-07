define(['knockout', 'underscore', 'uuid'], function (ko, _, uuid) {
    /**
    * A viewmodel used for generic widgets
    *
    * @constructor
    * @name WidgetViewModel
    *
    * @param  {string} params - a configuration object
    */
    var WidgetViewModel = function(params) {
        var self = this;
        this.state = params.state || 'form';
        var expanded = params.expanded || ko.observable(false);
        var nodeid = params.node ? params.node.nodeid : uuid.generate();
        this.expanded = ko.computed({
            read: function() {
                return nodeid === expanded();
            },
            write: function(val) {
                if (val) {
                    expanded(nodeid);
                } else {
                    expanded(false);
                }
            }
        });
        this.value = params.value || ko.observable(null);
        this.formData = params.formData || new FormData();
        this.form = params.form || null;
        this.tile = params.tile || null;
        this.results = params.results || null;
        this.displayValue = ko.computed(function() {
            return ko.unwrap(self.value);
        });
        this.disabled = params.disabled || ko.observable(false);
        this.node = params.node || null;
        this.configForm = params.configForm || false;
        this.config = params.config || ko.observable({});
        this.configObservables = params.configObservables || {};
        this.configKeys = params.configKeys || [];
        this.configKeys.push('label');
        this.configKeys.push('required');
        if (this.node) {
            this.required = this.node.isrequired;
        }
        if (typeof this.config !== 'function') {
            this.config = ko.observable(this.config);
        }

        var subscribeConfigObservable = function (obs, key) {
            self[key] = obs;

            self[key].subscribe(function(val) {
                var configObj = self.config();
                configObj[key] = val;
                self.config(configObj);
            });

            self.config.subscribe(function(val) {
                if (val[key] !== self[key]()) {
                    self[key](val[key]);
                }
            });
        };
        _.each(this.configObservables, subscribeConfigObservable);
        _.each(this.configKeys, function(key) {
            var obs = ko.observable(self.config()[key]);
            subscribeConfigObservable(obs, key);
        });

        if (ko.isObservable(this.defaultValue)) {
            var defaultValue = this.defaultValue();
            if (this.tile && this.tile.tileid() == "" && defaultValue != null && defaultValue != "") {
                this.value(defaultValue);
            }

            if (!self.form) {
                if (ko.isObservable(self.value)) {
                    self.value.subscribe(function(val){
                        if (self.defaultValue() != val) {
                            self.defaultValue(val)
                        };
                    });
                    self.defaultValue.subscribe(function(val){
                        if (self.value() != val) {
                            self.value(val)
                        };
                    });
                }
            };
        };
    };
    return WidgetViewModel;
});
