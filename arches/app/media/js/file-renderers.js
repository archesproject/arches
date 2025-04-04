import { loadComponentDependencies } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let fileRenderers;
try {        
    const fileRendererDataHTML = document.querySelector('#fileRendererData');
    const fileRendererData = fileRendererDataHTML.getAttribute('fileRenderers');
    fileRenderers = JSON.parse(removeTrailingCommaFromObject(fileRendererData));

    loadComponentDependencies(Object.values(fileRenderers).map(value => value['component']));
} catch (error) {
    console.error(error);
}

export default fileRenderers