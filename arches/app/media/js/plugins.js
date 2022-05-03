define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const pluginsDataHTML = document.querySelector('#pluginsData');
    const pluginsData = pluginsDataHTML.getAttribute('plugins');
    const plugins = JSON.parse(removeTrailingCommaFromObject(pluginsData));

    Object.keys(plugins).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${plugins[key]['component']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${plugins[key]['component']}`);
        }
    });

    return plugins;
});