define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {
        const graphPublicationDataHTML = document.querySelector('#graphPublicationData');
        const graphPublicationData = graphPublicationDataHTML.getAttribute('graphPublicationData');
    
        const parsedGraphPublicationData = JSON.parse(removeTrailingCommaFromObject(graphPublicationData));
    
        return parsedGraphPublicationData;
    } catch (error) {
        console.error(error);
    }
});