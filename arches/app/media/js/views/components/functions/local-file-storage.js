define(['knockout', 
        'knockout-mapping',
        'viewmodels/function', 
        'bindings/chosen'], 
function (ko, koMapping, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/local-file-storage', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated")}, 300);
        },
        template: {
            require: 'text!templates/views/components/functions/local-file-storage.htm'
        }
    });
})