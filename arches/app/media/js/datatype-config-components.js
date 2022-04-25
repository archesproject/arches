define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const datatypeConfigComponentDataHTML = document.querySelector('#datatypeConfigComponentData');
    const datatypeConfigComponentData = datatypeConfigComponentDataHTML.getAttribute('datatypeConfigComponents');
    const datatypeConfigComponents = JSON.parse(removeTrailingCommaFromObject(datatypeConfigComponentData));

    Object.keys(datatypeConfigComponents).forEach((key) => {
        require(`./${datatypeConfigComponents[key]['configcomponent']}`);
    });

    return datatypeConfigComponents;
});