import { registerComponentPaths } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let reportTemplates
try {        
    const reportTemplateDataHTML = document.querySelector('#reportTemplateData');
    const reportTemplateData = reportTemplateDataHTML.getAttribute('reportTemplates');
    reportTemplates = JSON.parse(removeTrailingCommaFromObject(reportTemplateData));

    registerComponentPaths(reportTemplates, 'componentname', 'component');
} catch (error) {
    console.error(error);
}

export default reportTemplates;