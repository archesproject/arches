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
            self[key] = ko.observable(self.config()[key]);

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
        });
    };
    return WidgetViewModel;
});
