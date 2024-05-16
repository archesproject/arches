define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const reportTemplateDataHTML = document.querySelector('#reportTemplateData');
        const reportTemplateData = reportTemplateDataHTML.getAttribute('reportTemplates');
        const reportTemplates = JSON.parse(removeTrailingCommaFromObject(reportTemplateData));
    
        loadComponentDependencies(Object.values(reportTemplates).map(value => value['component']));
    
        return reportTemplates;
    } catch (error) {
        console.error(error);
    }
});