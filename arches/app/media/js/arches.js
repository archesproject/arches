define([], function () {
    function buildUrls() {
        function removeWhitespace(string){
            return string.replace(/(\r\n|\n|\r)/gm, "");
        }
        
        function acceptUserInput(url){
            return function(input) {
                return url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', input);
            };
        }
    
        const archesData = document.querySelector('#arches-data');
    
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

    return {
        urls: buildUrls(),
    };
});