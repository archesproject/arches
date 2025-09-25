function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedGraphFunctionsData;
try {        
    const graphFunctionsDataHTML = document.querySelector('#graphFunctionsData');
    const graphFunctionsData = graphFunctionsDataHTML.getAttribute('graphFunctionsData');

    parsedGraphFunctionsData = JSON.parse(removeTrailingCommaFromObject(graphFunctionsData));
} catch (error) {
    console.error(error);
}

export default parsedGraphFunctionsData;
