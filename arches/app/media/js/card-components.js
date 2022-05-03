define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const cardComponentDataHTML = document.querySelector('#cardComponentData');
    const cardComponentData = cardComponentDataHTML.getAttribute('cardComponents');
    const cardComponents = JSON.parse(removeTrailingCommaFromObject(cardComponentData));

    Object.keys(cardComponents).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${cardComponents[key]['component']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${cardComponents[key]['component']}`);
        }
    });

    return cardComponents;
});