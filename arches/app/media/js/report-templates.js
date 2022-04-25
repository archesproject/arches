define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const reportTemplateDataHTML = document.querySelector('#reportTemplateData');
    const reportTemplateData = reportTemplateDataHTML.getAttribute('reportTemplates');
    const reportTemplates = JSON.parse(removeTrailingCommaFromObject(reportTemplateData));

    Object.keys(reportTemplates).forEach((key) => {
        require(`./${reportTemplates[key]['component']}`);
    });

    return reportTemplates;
});