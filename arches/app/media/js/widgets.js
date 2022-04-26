define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const widgetDataHTML = document.querySelector('#widgetData');
    const widgetData = widgetDataHTML.getAttribute('widgets');

    const widgets = JSON.parse(removeTrailingCommaFromObject(widgetData));

    // SAMPLE WIDGET HAS BAD TEMPLATE REQUIRE
    delete widgets['6cf125cc-a253-43ce-8d3c-7f791124bca9']


    Object.keys(widgets).forEach((key) => {
        require(`./${widgets[key]['component']}`);
    });

    return widgets;
});