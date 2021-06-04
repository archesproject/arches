define([
    'knockout',
], function(ko) {
    var viewModel = function(params){
        this.loading = ko.observable(true);

        console.log("resource summary", this, params)
    };
    ko.components.register('resource-summary', {
        viewModel: viewModel,
        template: { 
            require: 'text!templates/views/components/resource-summary.htm' 
        }
    });
});
