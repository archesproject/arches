define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const resourceEditHistoryDataHTML = document.querySelector('#resourceEditHistoryData');
    const resourceEditHistoryData = resourceEditHistoryDataHTML.getAttribute('resourceEditHistoryData');

    const parsedResourceEditHistoryData = JSON.parse(removeTrailingCommaFromObject(resourceEditHistoryData));

    return parsedResourceEditHistoryData;
});