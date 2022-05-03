define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const searchComponentDataHTML = document.querySelector('#searchComponentData');
    const searchComponentData = searchComponentDataHTML.getAttribute('searchComponents');
    const searchComponents = JSON.parse(removeTrailingCommaFromObject(searchComponentData));

    Object.keys(searchComponents).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${searchComponents[key]['componentpath']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${searchComponents[key]['componentpath']}`);
        }
    });

    return searchComponents;
});