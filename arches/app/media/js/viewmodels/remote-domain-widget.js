define([
    'jquery',
    'underscore',
    'viewmodels/domain-widget'
], function ($, _, DomainWidgetViewModel) {
    /**
    * A viewmodel used for remote domain widgets
    *
    * @constructor
    * @name RemoteDomainWidgetViewModel
    *
    * @param  {string} params - a configuration object
    */
    var RemoteDomainWidgetViewModel = function(params) {
        var self = this;

        params.configKeys = _.union(['options', 'url'], params.configKeys);

        DomainWidgetViewModel.apply(this, [params]);

        this.getOptions = function (url) {
            var self = this;
            if (url) {
                $.ajax({
                    url: url,
                    dataType: 'json'
                }).done(function(data) {
                    self.options(data);
                });
            }
        }

        this.url.subscribe(function(url) {
            this.getOptions(url);
        }, this);

        this.getOptions(this.url());
    };

    return RemoteDomainWidgetViewModel;
});
