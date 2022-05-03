define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const resourceTypeDataHTML = document.querySelector('#resourceTypeData');
    const resourceTypeData = resourceTypeDataHTML.getAttribute('resourceTypes');
    const resourceTypes = JSON.parse(removeTrailingCommaFromObject(resourceTypeData));

    Object.keys(resourceTypes).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${resourceTypes[key]['component']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${resourceTypes[key]['component']}`);
        }
    });

    return resourceTypes;
});