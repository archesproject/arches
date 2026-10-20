import { registerComponentPaths } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let searchComponents;
try {     
    const searchComponentDataHTML = document.querySelector('#searchComponentData');
    const searchComponentData = searchComponentDataHTML.getAttribute('searchComponents');
    searchComponents = JSON.parse(removeTrailingCommaFromObject(searchComponentData));

    registerComponentPaths(searchComponents, 'componentname', 'componentpath');
} catch (error) {
    console.error(error);
}

export default searchComponents;