define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const cardComponentDataHTML = document.querySelector('#cardComponentData');
    const cardComponentData = cardComponentDataHTML.getAttribute('cardComponents');
    const cardComponents = JSON.parse(removeTrailingCommaFromObject(cardComponentData));

    const foo = Object.keys(cardComponents).reduce((acc, key) => {
        acc.push(cardComponents[key]['component']);
        return acc;
    }, []);

    console.log(foo)
    console.log(foo[0] === 'views/components/cards/default')
    require('views/components/cards/default');

    return {...cardComponents};
});