define([
    'knockout',
    'views/base-manager',
], function(ko, BaseManagerView) {
    const pluginDataHTML = document.querySelector('#pluginData');
    const pluginData = JSON.parse(pluginDataHTML.getAttribute('pluginData'));

    const data = pluginData['plugin_json'];
    const plugins = pluginData['plugins_json'];

    plugins.forEach((plugin) => {
        try {  // first try to load project path
            require(`../../../../../../sfplanning/sfplanning/media/js/${plugin['component']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`../${plugin['component']}`);
        }
    });

    console.log("DS()", data, plugins)

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
