define([
    'views/base-manager',
    'plugin-data'
], function(BaseManagerView, data) {
    return new BaseManagerView({
        viewModel: {
            plugin: data
        }
    });
});
