function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedGraphSettingsData;
try {        
    const graphSettingsDataHTML = document.querySelector('#graphSettingsData');
    const graphSettingsData = graphSettingsDataHTML.getAttribute('graphSettingsData');

    parsedGraphSettingsData = JSON.parse(removeTrailingCommaFromObject(graphSettingsData));
} catch (error) {
    console.error(error);
}

export default parsedGraphSettingsData;
