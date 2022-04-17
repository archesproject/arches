define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const cardComponentDataHTML = document.querySelector('#cardComponentData');
    const cardComponentData = cardComponentDataHTML.getAttribute('cardComponents');
    const cardComponents = JSON.parse(removeTrailingCommaFromObject(cardComponentData));

    Object.keys(cardComponents).forEach((key) => {
        require(`./${cardComponents[key]['component']}.js`);
    });

    return {...cardComponents};
});