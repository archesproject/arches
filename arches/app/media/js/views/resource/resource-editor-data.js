function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

function forceDoubleQuotes(string) {
    return string.replace(/'/g, '"');
}

let parsedResourceEditorData;
try {        
    const resourceEditorDataHTML = document.querySelector('#resourceEditorData');
    const resourceEditorData = resourceEditorDataHTML.getAttribute('resourceEditorData');

    parsedResourceEditorData = JSON.parse(removeTrailingCommaFromObject(resourceEditorData));
    parsedResourceEditorData["relationship_types"] = JSON.parse(forceDoubleQuotes(parsedResourceEditorData["relationship_types"]));
    parsedResourceEditorData["creator"] = JSON.parse(parsedResourceEditorData["creator"]);
    parsedResourceEditorData["userisreviewer"] = Boolean(parsedResourceEditorData["userisreviewer"] === "True");
    parsedResourceEditorData["useriscreator"] = ["true", "True"].includes(parsedResourceEditorData["useriscreator"]);
} catch (error) {
    console.error(error);
}

export default parsedResourceEditorData;
