define([], function () {
    const archesData = document.querySelector('#arches-data');

    function removeWhitespace(string){
        return string.replace(/(\r\n|\n|\r)/gm, "");
    }
    
    function acceptUserInput(url){
        return function(input) {
            return url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', input)
        }
    }

    const urls = JSON.parse(removeWhitespace(archesData.getAttribute('urls') || ''));
    const userInputUrls = JSON.parse(removeWhitespace(archesData.getAttribute('userInputUrls') || ''));

    const formattedUserInputUrls = Object.keys(userInputUrls).reduce((acc, urlName) => {
        acc[urlName] = acceptUserInput(userInputUrls[urlName]);
        return acc;
    }, {});

    const unorderedUrls = { ...urls, ...formattedUserInputUrls };

    const orderedUrls = Object.keys(unorderedUrls).sort().reduce((acc, key) => {         
        acc[key] = unorderedUrls[key]; 
        return acc;
    }, {});
    
    console.log(orderedUrls)
    
    return {
        urls: orderedUrls,
    };
});