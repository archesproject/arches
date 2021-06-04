define([
    'knockout',
], function(ko) {
    var viewModel = function(){
        this.loading = ko.observable(true);
    };
    ko.components.register('resource-summary', {
        viewModel: viewModel,
        template: { 
            require: 'text!templates/views/components/resource-summary.htm' 
        }
    });
});
