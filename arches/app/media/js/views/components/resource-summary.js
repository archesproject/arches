define([
    'knockout',
    'views/components/foo'
], function(ko) {
    var viewModel = function(params){
        this.loading = ko.observable(false);

        this.fooCache = ko.observable({});

        console.log("resource summary", this, params)
    };
    ko.components.register('resource-summary', {
        viewModel: viewModel,
        template: { 
            require: 'text!templates/views/components/resource-summary.htm' 
        }
    });
});
