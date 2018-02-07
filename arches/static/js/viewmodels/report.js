define(['knockout', 'underscore', 'moment', 'bindings/let'], function (ko, _, moment) {
    var ReportViewModel = function(params) {
        var self = this;
        this.report = params.report || ko.observable(null);
        this.reportDate = moment().format('MMMM D, YYYY');
        this.configForm = params.configForm || false;
        this.configType = params.configType || 'header';

        this.config = params.report.configJSON || ko.observable({});
        this.configObservables = params.configObservables || {};
        this.configKeys = params.configKeys || [];
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
            var obs;
            if (Array.isArray(self.config()[key])) {
                obs = ko.observableArray(self.config()[key]);
            } else {
                obs = ko.observable(self.config()[key]);
            }
            subscribeConfigObservable(obs, key);
        });
    };
    return ReportViewModel;
});
