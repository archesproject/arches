import { loadComponentDependencies } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let datatypeConfigComponents;
try {
    const datatypeConfigComponentDataHTML = document.querySelector('#datatypeConfigComponentData');
    const datatypeConfigComponentData = datatypeConfigComponentDataHTML.getAttribute('datatypeConfigComponents');
    datatypeConfigComponents = JSON.parse(removeTrailingCommaFromObject(datatypeConfigComponentData));

    loadComponentDependencies(Object.values(datatypeConfigComponents).map(value => value['configcomponent']));
} 
catch (error) {
    console.error(error);
}

export default datatypeConfigComponents;