define([
    'views/base-manager',
    'plugin-data'
], function(BaseManagerView, data) {
    console.log(data);
    return new BaseManagerView({
        viewModel: {
            plugin: data
        }
    });
});
