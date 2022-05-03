define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const geocoderTemplateDataHTML = document.querySelector('#geocoderTemplateData');
    const geocoderTemplateData = geocoderTemplateDataHTML.getAttribute('geocoderTemplates');
    const geocoderTemplates = JSON.parse(removeTrailingCommaFromObject(geocoderTemplateData));

    Object.keys(geocoderTemplates).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${geocoderTemplates[key]['component']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${geocoderTemplates[key]['component']}`);
        }
    });

    return geocoderTemplates;
});