define([
    'knockout',
    'views/base-manager',
    'views/plugin-data',
    'plugins'
], function(ko, BaseManagerView, data) {
    if (!data.config) data.config = {};
    
    data.config.loading = ko.observable(false);
    data.config.alert = ko.observable(null);
    data.config.plugin = data;

    return new BaseManagerView({
        viewModel: {
            loading: data.config.loading,
            alert: data.config.alert,
            plugin: data
        }
    });
});
