function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let graphBaseDataJSON;
try {        
    const graphBaseDataHTML = document.querySelector('#graphBaseData');
    const graphBaseData = graphBaseDataHTML.getAttribute('graphBaseData');
    
    graphBaseDataJSON = JSON.parse(removeTrailingCommaFromObject(graphBaseData));
} catch (error) {
    console.error(error);
}

export default graphBaseDataJSON;
