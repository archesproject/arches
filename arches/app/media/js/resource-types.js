define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const resourceTypeDataHTML = document.querySelector('#resourceTypeData');
    const resourceTypeData = resourceTypeDataHTML.getAttribute('resourceTypes');
    const resourceTypes = JSON.parse(removeTrailingCommaFromObject(resourceTypeData));

    console.log(resourceTypes)

    Object.keys(resourceTypes).forEach((key) => {
        require(`./${resourceTypes[key]['component']}`);
    });

    return resourceTypes;
});