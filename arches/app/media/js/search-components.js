define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {     
        const searchComponentDataHTML = document.querySelector('#searchComponentData');
        const searchComponentData = searchComponentDataHTML.getAttribute('searchComponents');
        const searchComponents = JSON.parse(removeTrailingCommaFromObject(searchComponentData));
    
        loadComponentDependencies(Object.values(searchComponents).map(value => value['componentpath']));
    
        return searchComponents;
    } catch (error) {
        console.error(error);
    }
});