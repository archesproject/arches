define(['knockout', 'underscore'], function (ko, _) {
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
        this.value = params.value || ko.observable(null);
        this.disabled = params.disabled || ko.observable(false);
        this.configForm = params.configForm || false;
        this.config = params.config || ko.observable({});
        this.configObservables = params.configObservables || {};
        this.configKeys = params.configKeys || [];
        this.configKeys.push('label');
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
    };
    return WidgetViewModel;
});
