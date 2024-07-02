define([
    'knockout',
    'underscore',
    'uuid',
    'utils/dispose'
], function(ko, _, uuid, dispose) {
    /**
    * A viewmodel used for generic widgets
    *
    * @constructor
    * @name WidgetViewModel
    *
    * @param  {string} params - a configuration object
    */
    var WidgetViewModel = function(params) {
        this.externalObservables = ['value', 'config', 'expanded', 'defaultValueSubscription', 'valueSubscription'];
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
        this.formData = params.formData || null;
        this.form = params.form || null;
        this.tile = params.tile || null;
        this.widget = params.widget || null;
        this.inResourceEditor = (typeof params.inResourceEditor === "boolean" ? params.inResourceEditor : null);
        this.results = params.results || null;
        this.hideEmptyNodes = params.hideEmptyNodes;
        this.displayValue = ko.computed(function() {
            if (self.value.value) {
                return ko.unwrap(self.value.value);
            }
            else {
                return ko.unwrap(self.value);
            }
        });
        this.disabled = params.disabled || ko.observable(false);
        this.node = params.node || null;
        this.configForm = params.configForm || false;
        this.config = params.config || ko.observable({});
        this.configObservables = params.configObservables || {};
        this.configKeys = params.configKeys || [];
        this.configKeys.push('label');
        this.configKeys.push('required');
        this.valueProperties = params.valueProperties || [];
        if (this.node) {
            this.required = this.node.isrequired;
        }
        if (typeof this.config !== 'function') {
            this.config = ko.observable(this.config);
        }

        this.nodeCssClasses = ko.pureComputed(function() {
            return [ko.unwrap(self.node?.alias),
                self.node?.graph?.attributes?.slug,
                self.widget?.widgetLookup[ko.unwrap(self.widget?.widget_id)].name
                ].join(" ").trim();
        });

        this.disposables = [];

        var subscribeConfigObservable = function(obs, key) {
            self[key] = obs;

            var forwardSubscription = self[key].subscribe(function(val) {
                var configObj = self.config();
                configObj[key] = val;
                self.config(configObj);
            });

            var reverseSubscription = self.config.subscribe(function(val) {
                if (val[key] !== self[key]()) {
                    self[key](val[key]);
                }
            });
            self.disposables.push(forwardSubscription);
            self.disposables.push(reverseSubscription);
        };
        _.each(this.configObservables, subscribeConfigObservable);
        _.each(this.configKeys, function(key) {
            var obs = ko.observable(self.config()[key]);
            subscribeConfigObservable(obs, key);
        });

        if (ko.isObservable(this.value) && ko.isObservable(this.defaultValue)) {
            var defaultValue = this.defaultValue();
            if (this.tile && !this.tile.noDefaults && !ko.unwrap(this.tile.dirty) && ko.unwrap(this.tile.tileid) == "" && defaultValue != null && defaultValue != "") {
                this.value(defaultValue);
            }

            if (!self.form) {
                if (ko.isObservable(self.value)) {
                    self.valueSubscription = self.value.subscribe(function(val){
                        if (self.defaultValue() != val) {
                            self.defaultValue(val);
                        }
                    });
                    self.defaultValueSubscription = self.defaultValue.subscribe(function(val){
                        if (self.value() != val) {
                            self.value(val);
                        }
                    });
                }
            }
        }

        this.valueProperties.forEach(function(property) {
            if (ko.isObservable(self.value)){
                self[property] = ko.observable();
                self[property].subscribe(function() {
                    self.value(
                        self.valueProperties.reduce(
                            function(data, property){
                                data[property] = self[property]();
                                return data;
                            }, {}
                        )
                    );
                }, this);
            } else {
                self[property] = self.value[property];
            }
        });

        this.disposables.push(this.defaultValueSubscription);
        this.disposables.push(this.valueSubscription);

        this.onInit = params.onInit;
        if (typeof this.onInit === 'function') {
            this.onInit();
        }

        this.dispose = function(){
            //console.log('disposing ' + self.constructor.name);
            dispose(self);
        };
    };

    return WidgetViewModel;
});
