define(['utils/set-csrf-token'], function() {
    function removeTrailingCommaFromArray(string) {
        return string.replace(/,]*$/, "]");
    }
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }
    function removeWhitespace(string){
        return string.replace(/(\r\n|\n|\r)/gm, "");
    }
    
    function buildUrls() {
        function acceptUserInput(url){
            return function(input) {
                return url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', input);
            };
        }

        const staticUrls = JSON.parse(removeWhitespace(archesData.getAttribute('staticUrls') || ''));
        const dynamicUrls = JSON.parse(removeWhitespace(archesData.getAttribute('dynamicUrls') || ''));
        const userInputUrls = JSON.parse(removeWhitespace(archesData.getAttribute('userInputUrls') || ''));

        // BEGIN NON-STANDARD FORMATS
        const mvtUrl = archesData.getAttribute('mvtUrl');
        const resourceDataUrl = archesData.getAttribute('resourceDataUrl');
        const apiSearchComponentDataUrl = archesData.getAttribute('apiSearchComponentDataUrl');
        const validateJsonUrl = archesData.getAttribute('validateJsonUrl');
        // END NON_STANDARD FORMATS

        const formattedDynamicUrls = Object.keys(dynamicUrls).reduce((acc, urlName) => {
            acc[urlName] = dynamicUrls[urlName].replace("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "");
            return acc;
        }, {});
    
        const formattedUserInputUrls = Object.keys(userInputUrls).reduce((acc, urlName) => {
            acc[urlName] = acceptUserInput(userInputUrls[urlName]);
            return acc;
        }, {});
    
        const unorderedUrls = { 
            ...staticUrls, 
            ...formattedDynamicUrls, 
            ...formattedUserInputUrls,
            "mvt": function(nodeid) {
                return decodeURI(mvtUrl).replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', nodeid);
            },
            "resource_data": resourceDataUrl.replace(/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/g, ""),
            "api_search_component_data": apiSearchComponentDataUrl.replace('aaaa', ''),
            "validatejson": validateJsonUrl.replace('aaaa', ''),
        };
    
        const orderedUrls = Object.keys(unorderedUrls).sort().reduce((acc, key) => {         
            acc[key] = unorderedUrls[key]; 
            return acc;
        }, {});

        return orderedUrls;
    }

    const archesData = document.querySelector('#arches-data');

    return {
        celeryRunning: archesData.getAttribute('celeryRunning'),
        conceptCollections: JSON.parse(removeTrailingCommaFromArray(archesData.getAttribute('conceptCollections'))),
        confirmAllResourceDelete: JSON.parse(archesData.getAttribute('confirmAllResourceDelete')),
        confirmGraphDelete: JSON.parse(archesData.getAttribute('confirmGraphDelete')),
        confirmMaplayerDelete: JSON.parse(archesData.getAttribute('confirmMaplayerDelete')),
        confirmNav: JSON.parse(archesData.getAttribute('confirmNav')),
        confirmResourceDelete: JSON.parse(archesData.getAttribute('confirmResourceDelete')),
        confirmSurveyDelete: JSON.parse(archesData.getAttribute('confirmSurveyDelete')),
        exportHtmlTemplates: JSON.parse(removeTrailingCommaFromArray(archesData.getAttribute('exportHtmlTemplates'))),
        geocoderDefault: archesData.getAttribute('geocoderDefault'),
        geocoderPlaceholder: archesData.getAttribute('geocoderPlaceholder'),
        geoCodingProviders: JSON.parse(removeTrailingCommaFromArray(archesData.getAttribute('geoCodingProviders'))),
        graphImportFailed: JSON.parse(archesData.getAttribute('graphImportFailed')),
        graphs: JSON.parse(archesData.getAttribute('graphs')),
        hexBinBounds: JSON.parse(archesData.getAttribute('hexBinBounds')),
        hexBinSize: JSON.parse(archesData.getAttribute('hexBinSize')),
        mapDefaultX: JSON.parse(archesData.getAttribute('mapDefaultX')),
        mapDefaultY: JSON.parse(archesData.getAttribute('mapDefaultY')),
        mapDefaultZoom: JSON.parse(archesData.getAttribute('mapDefaultZoom')),
        mapDefaultMinZoom: JSON.parse(archesData.getAttribute('mapDefaultMinZoom')),
        mapDefaultMaxZoom: JSON.parse(archesData.getAttribute('mapDefaultMaxZoom')),
        mapboxApiKey: archesData.getAttribute('mapboxApiKey'),
        mapboxGlyphs: archesData.getAttribute('mapboxGlyphs'),
        mapboxSprites: archesData.getAttribute('mapboxSprites'),
        mapLayers: JSON.parse(removeTrailingCommaFromArray(archesData.getAttribute('mapLayers'))),
        mapMarkers: JSON.parse(removeTrailingCommaFromArray(archesData.getAttribute('mapMarkers'))),
        mapSources: JSON.parse(removeTrailingCommaFromObject(archesData.getAttribute('mapSources'))),
        preferredCoordinateSystems: JSON.parse(archesData.getAttribute('preferredCoordinateSystems')),
        requestFailed: JSON.parse(archesData.getAttribute('requestFailed')),
        resourceCopyFailed: JSON.parse(archesData.getAttribute('resourceCopyFailed')),
        resourceCopySuccess: JSON.parse(archesData.getAttribute('resourceCopySuccess')),
        resourceHasUnpublishedGraph: JSON.parse(archesData.getAttribute('resourceHasUnpublishedGraph')),
        resources: JSON.parse(removeTrailingCommaFromArray(archesData.getAttribute('resources'))),
        translations: JSON.parse(removeWhitespace(archesData.getAttribute('translations'))),
        urls: buildUrls(),
        userEmail: archesData.getAttribute('userEmail'),
        useSemanticRelationships: JSON.parse(archesData.getAttribute('useSemanticRelationships')),
        version: archesData.getAttribute('version'),
    };
});