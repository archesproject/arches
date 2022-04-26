define(['require'], function (require) {
    function removeTrailingCommaFromObject(string) {
        return string.replace(/,\s*}*$/, "}");
    }

    const widgetDataHTML = document.querySelector('#widgetData');
    const widgetData = widgetDataHTML.getAttribute('widgets');

    const widgets = JSON.parse(removeTrailingCommaFromObject(widgetData));

    Object.keys(widgets).forEach((key) => {
        require('views/components/widgets/sample-widget');
        require('views/components/widgets/resource-instance-select');
        
        try {  // first try to load directory path
            require(`../../../../../sfplanning/sfplanning/media/js/${widgets[key]['component']}`);
        }
        catch(e) {  // if directory path fails, load arches-core path
            require(`./${widgets[key]['component']}`);
        }
    });

    return widgets;
});