define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    function forceDoubleQuotes(string) {
        return string.replace(/'/g, '"');
    }

    try {        
        const graphDesignerDataHTML = document.querySelector('#graphDesignerData');
        const graphDesignerData = graphDesignerDataHTML.getAttribute('graphDesignerData');
    
        const parsedGraphDesignerData = JSON.parse(removeTrailingCommaFromObject(graphDesignerData));
        parsedGraphDesignerData.restrictedNodegroups = JSON.parse(forceDoubleQuotes(parsedGraphDesignerData.restrictedNodegroups));
        parsedGraphDesignerData.ontology_namespaces = JSON.parse(forceDoubleQuotes(parsedGraphDesignerData.ontology_namespaces));
    
        return parsedGraphDesignerData;
    } catch (error) {
        console.error(error);
    }
});