import { registerComponentPaths } from "utils/load-component-dependencies";

function removeTrailingCommaFromObject(string) {
    return string.replace(/,\s*}*$/, "}");
}

let widgets;
try {        
    const widgetDataHTML = document.querySelector('#widgetData');
    const widgetData = widgetDataHTML.getAttribute('widgets');
    widgets = JSON.parse(removeTrailingCommaFromObject(widgetData));

    registerComponentPaths(widgets, 'name', 'component');
} catch (error) {
    console.error(error);
}

export default widgets;