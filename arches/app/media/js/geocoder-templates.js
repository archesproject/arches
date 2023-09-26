define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const geocoderTemplateDataHTML = document.querySelector('#geocoderTemplateData');
    const geocoderTemplateData = geocoderTemplateDataHTML.getAttribute('geocoderTemplates');
    const geocoderTemplates = JSON.parse(removeTrailingCommaFromObject(geocoderTemplateData));

    loadComponentDependencies(Object.values(geocoderTemplates).map(value => value['component']));

    return geocoderTemplates;
});