define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const searchComponentDataHTML = document.querySelector('#searchComponentData');
    const searchComponentData = searchComponentDataHTML.getAttribute('searchComponents');
    const searchComponents = JSON.parse(removeTrailingCommaFromObject(searchComponentData));

    console.log(searchComponents)

    Object.keys(searchComponents).forEach((key) => {
        require(`./${searchComponents[key]['componentpath']}`);
    });

    return searchComponents;
});