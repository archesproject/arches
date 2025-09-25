import { loadComponentDependencies } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let reportTemplates
try {        
    const reportTemplateDataHTML = document.querySelector('#reportTemplateData');
    const reportTemplateData = reportTemplateDataHTML.getAttribute('reportTemplates');
    reportTemplates = JSON.parse(removeTrailingCommaFromObject(reportTemplateData));

    loadComponentDependencies(Object.values(reportTemplates).map(value => value['component']));
} catch (error) {
    console.error(error);
}

export default reportTemplates;