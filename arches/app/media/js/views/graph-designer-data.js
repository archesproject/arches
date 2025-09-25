function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

function forceDoubleQuotes(string) {
    return string.replace(/'/g, '"');
}

let parsedGraphDesignerData;
try {        
    const graphDesignerDataHTML = document.querySelector('#graphDesignerData');
    const graphDesignerData = graphDesignerDataHTML.getAttribute('graphDesignerData');

    parsedGraphDesignerData = JSON.parse(removeTrailingCommaFromObject(graphDesignerData));
    parsedGraphDesignerData.ontology_namespaces = JSON.parse(forceDoubleQuotes(parsedGraphDesignerData.ontology_namespaces));
} catch (error) {
    console.error(error);
}

export default parsedGraphDesignerData;
