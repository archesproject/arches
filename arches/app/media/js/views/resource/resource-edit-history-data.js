function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedResourceEditHistoryData;
try {        
    const resourceEditHistoryDataHTML = document.querySelector('#resourceEditHistoryData');
    const resourceEditHistoryData = resourceEditHistoryDataHTML.getAttribute('resourceEditHistoryData');

    parsedResourceEditHistoryData = JSON.parse(removeTrailingCommaFromObject(resourceEditHistoryData));
} catch (error) {
    console.error(error);
}

export default parsedResourceEditHistoryData;
