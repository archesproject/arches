define([], function() {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const graphFunctionsDataHTML = document.querySelector('#graphFunctionsData');
    const graphFunctionsData = graphFunctionsDataHTML.getAttribute('graphFunctionsData');

    const parsedGraphFunctionsData = JSON.parse(removeTrailingCommaFromObject(graphFunctionsData));

    return parsedGraphFunctionsData;
});