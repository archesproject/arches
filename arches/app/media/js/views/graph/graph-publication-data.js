function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedGraphPublicationData;
try {
    const graphPublicationDataHTML = document.querySelector('#graphPublicationData');
    const graphPublicationData = graphPublicationDataHTML.getAttribute('graphPublicationData');

    parsedGraphPublicationData = JSON.parse(removeTrailingCommaFromObject(graphPublicationData));
} catch (error) {
    console.error(error);
}

export default parsedGraphPublicationData;
