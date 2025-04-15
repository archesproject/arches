import { loadComponentDependencies } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let searchComponents;
try {     
    const searchComponentDataHTML = document.querySelector('#searchComponentData');
    const searchComponentData = searchComponentDataHTML.getAttribute('searchComponents');
    searchComponents = JSON.parse(removeTrailingCommaFromObject(searchComponentData));

    loadComponentDependencies(Object.values(searchComponents).map(value => value['componentpath']));
} catch (error) {
    console.error(error);
}

export default searchComponents;