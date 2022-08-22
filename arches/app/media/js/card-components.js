define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const cardComponentDataHTML = document.querySelector('#cardComponentData');
    const cardComponentData = cardComponentDataHTML.getAttribute('cardComponents');
    const cardComponents = JSON.parse(removeTrailingCommaFromObject(cardComponentData));

    loadComponentDependencies(Object.values(cardComponents).map(value => value['component']));

    return cardComponents;
});