define(['knockout',
        'knockout-mapping',
        'views/list',
        'viewmodels/function',
        'bindings/chosen'],
function (ko, koMapping, ListView, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/sample-function', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            console.log("Running a sample function")
            var self = this;
        },
        template: {
            require: 'text!functions/templates/required-nodes.htm'
        }
    });
})
