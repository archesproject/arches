define(['require'], function(require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const graphBaseDataHTML = document.querySelector('#graphBaseData');
    const graphBaseData = graphBaseDataHTML.getAttribute('graphBaseData');
    const graphBaseDataJSON = JSON.parse(removeTrailingCommaFromObject(graphBaseData));

    return graphBaseDataJSON;
});