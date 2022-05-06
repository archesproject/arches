define([
    'jquery',
    'underscore',
    'viewmodels/domain-widget'
], function($, _, DomainWidgetViewModel) {
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

        // to be used in widgets/extended view models to prep data for select
        var prepData = typeof params.prepData === 'function' ?
            params.prepData :
            function(data) { return data; };

        var getOptions = function(url) {
            if (url) {
                $.ajax({
                    url: url,
                    dataType: 'json'
                }).done(function(data) {
                    self.options(prepData(data));
                });
            }
        };

        this.url.subscribe(getOptions);
        getOptions(this.url());
    };

    return RemoteDomainWidgetViewModel;
});
