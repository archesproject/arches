define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const functionTemplateDataHTML = document.querySelector('#functionTemplateData');
    const functionTemplateData = functionTemplateDataHTML.getAttribute('functionTemplates');
    const functionTemplates = JSON.parse(removeTrailingCommaFromObject(functionTemplateData));

    Object.keys(functionTemplates).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${functionTemplates[key]['component']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${functionTemplates[key]['component']}`);
        }
    });

    return functionTemplates;
});