define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const geocoderTemplateDataHTML = document.querySelector('#geocoderTemplateData');
    const geocoderTemplateData = geocoderTemplateDataHTML.getAttribute('geocoderTemplates');
    const geocoderTemplates = JSON.parse(removeTrailingCommaFromObject(geocoderTemplateData));

    Object.keys(geocoderTemplates).forEach((key) => {
        require(`./${geocoderTemplates[key]['component']}`);
    });

    return geocoderTemplates;
});