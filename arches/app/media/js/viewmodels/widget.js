define(['knockout'], function (ko) {
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
        this.value = params.value || ko.observable(null);
        this.disabled = params.disabled || ko.observable(false);
        this.configForm = params.configForm || false;
        this.config = params.config || ko.observable({});
        this.configKeys = params.configKeys || [];
        if (typeof this.config !== 'function') {
            this.config = ko.observable(this.config);
        }
        this.label = this.config().label || ko.observable('');

        this.configKeys.forEach(function(key) {
            self[key] = ko.observable(self.config()[key])
                .extend({
                    updateConfig: {
                        config: self.config,
                        key: key
                    }
                });
        });
        
    };

    ko.extenders.updateConfig = function(target, opts) {
        target.subscribe(function(val) {
            var configObj = opts.config();
            configObj[opts.key] = val;
            opts.config(configObj);
        });

        opts.config.subscribe(function(val) {
            if (val[opts.key] !== target()) {
                target(val[opts.key]);
            }
        });

        return target;
    };
    return WidgetViewModel;
});
