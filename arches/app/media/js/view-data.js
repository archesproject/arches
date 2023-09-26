define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const viewDataHTML = document.querySelector('#viewData');
    const viewData = viewDataHTML.getAttribute('viewData');

    const parsedViewData = JSON.parse(removeTrailingCommaFromObject(viewData));
    parsedViewData['userCanEditResources'] = Boolean(parsedViewData['userCanEditResources'] === "True");
    parsedViewData['userCanReadResources'] = Boolean(parsedViewData['userCanReadResources'] === "True");

    return parsedViewData;
});