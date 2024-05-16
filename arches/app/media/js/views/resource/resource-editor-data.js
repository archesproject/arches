define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    function forceDoubleQuotes(string) {
        return string.replace(/'/g, '"');
    }

    try {        
        const resourceEditorDataHTML = document.querySelector('#resourceEditorData');
        const resourceEditorData = resourceEditorDataHTML.getAttribute('resourceEditorData');
    
        const parsedResourceEditorData = JSON.parse(removeTrailingCommaFromObject(resourceEditorData));
        parsedResourceEditorData["relationship_types"] = JSON.parse(forceDoubleQuotes(parsedResourceEditorData["relationship_types"]));
        parsedResourceEditorData["creator"] = JSON.parse(parsedResourceEditorData["creator"]);
        parsedResourceEditorData["userisreviewer"] = Boolean(parsedResourceEditorData["userisreviewer"] === "True");
        parsedResourceEditorData["useriscreator"] = ["true", "True"].includes(parsedResourceEditorData["useriscreator"]);
    
        return parsedResourceEditorData;
    } catch (error) {
        console.error(error);
    }
});