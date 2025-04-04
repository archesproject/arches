function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedPluginData;
try {        
    const pluginDataHTML = document.querySelector('#pluginData');
    const pluginData = pluginDataHTML.getAttribute('pluginData');

    parsedPluginData = JSON.parse(removeTrailingCommaFromObject(pluginData));
} catch (error) {
    console.error(error);
}

export default parsedPluginData;
