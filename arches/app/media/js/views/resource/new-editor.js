require([
    'knockout',
    'views/base-manager'
], function(ko, BaseManagerView) {
    var self = this;
    var loading = ko.observable(false);

    var pageView = new BaseManagerView({
        viewModel:{
            loading: loading
        }
    });
});
