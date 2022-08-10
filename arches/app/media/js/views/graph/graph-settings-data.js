define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const graphSettingsDataHTML = document.querySelector('#graphSettingsData');
    const graphSettingsData = graphSettingsDataHTML.getAttribute('graphSettingsData');

    const parsedGraphSettingsData = JSON.parse(removeTrailingCommaFromObject(graphSettingsData));

    return parsedGraphSettingsData;
});