import { loadComponentDependencies } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let geocoderTemplates;
try {        
    const geocoderTemplateDataHTML = document.querySelector('#geocoderTemplateData');
    const geocoderTemplateData = geocoderTemplateDataHTML.getAttribute('geocoderTemplates');
    geocoderTemplates = JSON.parse(removeTrailingCommaFromObject(geocoderTemplateData));

    loadComponentDependencies(Object.values(geocoderTemplates).map(value => value['component']));
} catch (error) {
    console.error(error);
}

export default geocoderTemplates;