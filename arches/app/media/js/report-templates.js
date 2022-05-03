define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const reportTemplateDataHTML = document.querySelector('#reportTemplateData');
    const reportTemplateData = reportTemplateDataHTML.getAttribute('reportTemplates');
    const reportTemplates = JSON.parse(removeTrailingCommaFromObject(reportTemplateData));

    Object.keys(reportTemplates).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${reportTemplates[key]['component']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${reportTemplates[key]['component']}`);
        }
    });

    return reportTemplates;
});