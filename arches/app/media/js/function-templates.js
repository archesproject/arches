define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const functionTemplateDataHTML = document.querySelector('#functionTemplateData');
    const functionTemplateData = functionTemplateDataHTML.getAttribute('functionTemplates');
    const functionTemplates = JSON.parse(removeTrailingCommaFromObject(functionTemplateData));
    
    loadComponentDependencies(Object.values(functionTemplates).map(value => value['component']));

    return functionTemplates;
});