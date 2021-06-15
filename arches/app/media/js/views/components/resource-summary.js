define([
    'knockout',
    'views/components/resource-report-abstract'
], function(ko) {
    var viewModel = function(params){
        this.loading = ko.observable(false);

        console.log("resource summary", this, params)
    };
    ko.components.register('resource-summary', {
        viewModel: viewModel,
        template: { 
            require: 'text!templates/views/components/resource-summary.htm' 
        }
    });
});
