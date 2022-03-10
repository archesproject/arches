define([
    'knockout',
    'views/base-manager',
], function(ko, BaseManagerView) {
    const data = window['plugin-data'];

    if (!data.config) data.config = {};
    data.config.loading = ko.observable(false);
    data.config.alert = ko.observable(null);
    return new BaseManagerView({
        viewModel: {
            loading: data.config.loading,
            alert: data.config.alert,
            plugin: data
        }
    });
});
