define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const graphManagerDataHTML = document.querySelector('#graphManagerData');
        const graphManagerData = graphManagerDataHTML.getAttribute('graphManagerData');
    
        const parsedGraphManagerData = JSON.parse(removeTrailingCommaFromObject(graphManagerData));
    
        return parsedGraphManagerData;
    } catch (error) {
        console.error(error);
    }
});