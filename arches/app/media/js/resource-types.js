function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let resourceTypes;
try {        
    const resourceTypeDataHTML = document.querySelector('#resourceTypeData');
    const resourceTypeData = resourceTypeDataHTML.getAttribute('resourceTypes');
    resourceTypes = JSON.parse(removeTrailingCommaFromObject(resourceTypeData));
} catch (error) {
    console.error(error);
}

export default resourceTypes;