define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    try {
        const cardComponentDataHTML = document.querySelector('#cardComponentData');
        const cardComponentData = cardComponentDataHTML.getAttribute('cardComponents');
        const cardComponents = JSON.parse(removeTrailingCommaFromObject(cardComponentData));
    
        loadComponentDependencies(Object.values(cardComponents).map(value => value['component']));

        return cardComponents;
    } catch (error) {
        console.error(error);
    }
});