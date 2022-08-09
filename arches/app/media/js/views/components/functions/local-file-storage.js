define([
    'jquery',
    'knockout', 
    'knockout-mapping',
    'viewmodels/function', 
    'bindings/chosen',
    'templates/views/components/functions/local-file-storage.htm'
], function($, ko, koMapping, FunctionViewModel, chosen, localFileStorageTemplate) {
    return ko.components.register('views/components/functions/local-file-storage', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated");}, 300);
        },
        template: localFileStorageTemplate,
    });
});