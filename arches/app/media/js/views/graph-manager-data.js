function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedGraphManagerData;
try {        
    const graphManagerDataHTML = document.querySelector('#graphManagerData');
    const graphManagerData = graphManagerDataHTML.getAttribute('graphManagerData');

    parsedGraphManagerData = JSON.parse(removeTrailingCommaFromObject(graphManagerData));
} catch (error) {
    console.error(error);
}

export default parsedGraphManagerData;
