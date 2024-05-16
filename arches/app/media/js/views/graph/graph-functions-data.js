define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const graphFunctionsDataHTML = document.querySelector('#graphFunctionsData');
        const graphFunctionsData = graphFunctionsDataHTML.getAttribute('graphFunctionsData');
    
        const parsedGraphFunctionsData = JSON.parse(removeTrailingCommaFromObject(graphFunctionsData));
    
        return parsedGraphFunctionsData;
    } catch (error) {
        console.error(error);
    }
});