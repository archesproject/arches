define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const resourceTypeDataHTML = document.querySelector('#resourceTypeData');
        const resourceTypeData = resourceTypeDataHTML.getAttribute('resourceTypes');
        const resourceTypes = JSON.parse(removeTrailingCommaFromObject(resourceTypeData));
    
        loadComponentDependencies(Object.values(resourceTypes).map(value => value['component']));
        
        return resourceTypes;
    } catch (error) {
        console.error(error);
    }
});