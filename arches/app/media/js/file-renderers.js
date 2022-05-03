define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const fileRendererDataHTML = document.querySelector('#fileRendererData');
    const fileRendererData = fileRendererDataHTML.getAttribute('fileRenderers');
    const fileRenderers = JSON.parse(removeTrailingCommaFromObject(fileRendererData));

    Object.keys(fileRenderers).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${fileRenderers[key]['component']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${fileRenderers[key]['component']}`);
        }
    });

    return fileRenderers;
});