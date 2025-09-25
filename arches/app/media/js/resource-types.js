import { loadComponentDependencies } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let resourceTypes;
try {        
    const resourceTypeDataHTML = document.querySelector('#resourceTypeData');
    const resourceTypeData = resourceTypeDataHTML.getAttribute('resourceTypes');
    resourceTypes = JSON.parse(removeTrailingCommaFromObject(resourceTypeData));

    loadComponentDependencies(Object.values(resourceTypes).map(value => value['component']));
} catch (error) {
    console.error(error);
}

export default resourceTypes;