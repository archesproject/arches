define(['knockout'], function (ko) {
    /**
    * A viewmodel used for generic widgets
    *
    * @constructor
    * @name WidgetViewModel
    *
    * @param  {string} params - a configuration object
    */
    var WidgetViewModel = function(params) {
        this.value = params.value;
        this.disabled = params.disabled;
        this.label = params.config.label;
    };
    return WidgetViewModel;
});
