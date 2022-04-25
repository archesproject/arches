define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const fileRendererDataHTML = document.querySelector('#fileRendererData');
    const fileRendererData = fileRendererDataHTML.getAttribute('fileRenderers');
    const fileRenderers = JSON.parse(removeTrailingCommaFromObject(fileRendererData));

    Object.keys(fileRenderers).forEach((key) => {
        require(`./${fileRenderers[key]['component']}`);
    });

    return fileRenderers;
});