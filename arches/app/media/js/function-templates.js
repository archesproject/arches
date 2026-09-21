import { registerComponentPaths } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let functionTemplates;
try {        
    const functionTemplateDataHTML = document.querySelector('#functionTemplateData');
    const functionTemplateData = functionTemplateDataHTML.getAttribute('functionTemplates');
    functionTemplates = JSON.parse(removeTrailingCommaFromObject(functionTemplateData));

    registerComponentPaths(functionTemplates, 'component', 'component');
} catch (error) {
    console.error(error);
}

export default functionTemplates;