define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const functionTemplateDataHTML = document.querySelector('#functionTemplateData');
        const functionTemplateData = functionTemplateDataHTML.getAttribute('functionTemplates');
        const functionTemplates = JSON.parse(removeTrailingCommaFromObject(functionTemplateData));
    
        loadComponentDependencies(
            Object.values(functionTemplates).reduce((acc, value) => {
                if (value['component']) {
                    acc.push(value['component']);
                }
                return acc;
            }, [])
        );
    
        return functionTemplates;
    } catch (error) {
        console.error(error);
    }
});