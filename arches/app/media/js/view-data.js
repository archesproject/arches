function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedViewData;
try {
    const viewDataHTML = document.querySelector('#viewData');
    const viewData = viewDataHTML.getAttribute('viewData');
    parsedViewData = JSON.parse(removeTrailingCommaFromObject(viewData));
    parsedViewData['userCanEditResources'] = Boolean(parsedViewData['userCanEditResources'] === "True");
    parsedViewData['userCanReadResources'] = Boolean(parsedViewData['userCanReadResources'] === "True");
} catch (error) {
    console.error(error);
}

export default parsedViewData;