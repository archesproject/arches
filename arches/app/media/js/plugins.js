import { registerComponentPaths } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let plugins;
try {        
    const pluginsDataHTML = document.querySelector('#pluginsData');
    const pluginsData = pluginsDataHTML.getAttribute('plugins');
    plugins = JSON.parse(removeTrailingCommaFromObject(pluginsData));

    registerComponentPaths(plugins, 'componentname', 'component');
} catch (error) {
    console.error(error);
}

export default plugins;