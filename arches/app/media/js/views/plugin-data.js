define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const pluginDataHTML = document.querySelector('#pluginData');
        const pluginData = pluginDataHTML.getAttribute('pluginData');
    
        const parsedPluginData = JSON.parse(removeTrailingCommaFromObject(pluginData));
    
        return parsedPluginData;
    } catch (error) {
        console.error(error);
    }
});