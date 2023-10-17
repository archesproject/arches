define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {
        const datatypeConfigComponentDataHTML = document.querySelector('#datatypeConfigComponentData');
        const datatypeConfigComponentData = datatypeConfigComponentDataHTML.getAttribute('datatypeConfigComponents');
        const datatypeConfigComponents = JSON.parse(removeTrailingCommaFromObject(datatypeConfigComponentData));
    
        loadComponentDependencies(Object.values(datatypeConfigComponents).map(value => value['configcomponent']));
    
        return datatypeConfigComponents;
    } 
    catch (error) {
        console.error(error);
    }
});