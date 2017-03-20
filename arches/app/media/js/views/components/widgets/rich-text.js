define(['knockout', 'underscore', 'viewmodels/widget', 'bindings/summernote'], function (ko, _, WidgetViewModel) {
    /**
    * registers a rich-text-widget component for use in forms
    * @function external:"ko.components".rich-text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    */
    return ko.components.register('rich-text-widget', {
        viewModel: function(params){
            WidgetViewModel.apply(this, [params]);
            this.value.subscribe(function(val){
                console.log(val)
            })
        },
        template: { require: 'text!widget-templates/rich-text' }
    });
});
