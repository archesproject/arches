define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const pluginDataHTML = document.querySelector('#pluginData');
    const pluginData = pluginDataHTML.getAttribute('pluginData');

    const parsedPluginData = JSON.parse(removeTrailingCommaFromObject(pluginData));

    return parsedPluginData;
});