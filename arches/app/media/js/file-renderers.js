define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const fileRendererDataHTML = document.querySelector('#fileRendererData');
        const fileRendererData = fileRendererDataHTML.getAttribute('fileRenderers');
        const fileRenderers = JSON.parse(removeTrailingCommaFromObject(fileRendererData));
    
        loadComponentDependencies(Object.values(fileRenderers).map(value => value['component']));
    
        return fileRenderers;
    } catch (error) {
        console.error(error);
    }
});