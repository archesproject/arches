define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const pluginsDataHTML = document.querySelector('#pluginsData');
        const pluginsData = pluginsDataHTML.getAttribute('plugins');
        const plugins = JSON.parse(removeTrailingCommaFromObject(pluginsData));
    
        loadComponentDependencies(Object.values(plugins).map(value => value['component']));
    
        return plugins;
    } catch (error) {
        console.error(error);
    }
});