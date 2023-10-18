define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {        
        const mapLayerManagerDataHTML = document.querySelector('#mapLayerManagerData');
        const mapLayerManagerData = mapLayerManagerDataHTML.getAttribute('mapLayerManagerData');
    
        const parsedMapLayerManagerData = JSON.parse(removeTrailingCommaFromObject(mapLayerManagerData));
    
        return parsedMapLayerManagerData;
    } catch (error) {
        console.error(error);
    }
});