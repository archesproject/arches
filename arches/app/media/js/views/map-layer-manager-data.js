function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let parsedMapLayerManagerData;
try {        
    const mapLayerManagerDataHTML = document.querySelector('#mapLayerManagerData');
    const mapLayerManagerData = mapLayerManagerDataHTML.getAttribute('mapLayerManagerData');

    parsedMapLayerManagerData = JSON.parse(removeTrailingCommaFromObject(mapLayerManagerData));
} catch (error) {
    console.error(error);
}

export default parsedMapLayerManagerData;