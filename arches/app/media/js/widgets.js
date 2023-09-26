define(['utils/load-component-dependencies'], function(loadComponentDependencies) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const widgetDataHTML = document.querySelector('#widgetData');
    const widgetData = widgetDataHTML.getAttribute('widgets');
    const widgets = JSON.parse(removeTrailingCommaFromObject(widgetData));

    loadComponentDependencies(Object.values(widgets).map(value => value['component']));

    return widgets;
});