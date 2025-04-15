import { loadComponentDependencies } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let cardComponents;
try {
    const cardComponentDataHTML = document.querySelector('#cardComponentData');
    const cardComponentData = cardComponentDataHTML.getAttribute('cardComponents');
    cardComponents = JSON.parse(removeTrailingCommaFromObject(cardComponentData));

    loadComponentDependencies(Object.values(cardComponents).map(value => value['component']));
} catch (error) {
    console.error(error);
}

export default cardComponents;