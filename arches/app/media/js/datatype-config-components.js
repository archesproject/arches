define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const datatypeConfigComponentDataHTML = document.querySelector('#datatypeConfigComponentData');
    const datatypeConfigComponentData = datatypeConfigComponentDataHTML.getAttribute('datatypeConfigComponents');
    const datatypeConfigComponents = JSON.parse(removeTrailingCommaFromObject(datatypeConfigComponentData));

    Object.keys(datatypeConfigComponents).forEach((key) => {
        try {  // first try to load project path
            require(`../../../../../sfplanning/sfplanning/media/js/${datatypeConfigComponents[key]['configcomponent']}`);
        }
        catch(e) {  // if project path fails, load arches-core path
            require(`./${datatypeConfigComponents[key]['configcomponent']}`);
        }
    });

    return datatypeConfigComponents;
});