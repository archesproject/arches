require([
    'jquery',
    'knockout',
    'views/base-manager',
    'bindings/resizable-sidebar'
], function($, ko, BaseManagerView) {
    var self = this;
    var loading = ko.observable(false);

    var pageView = new BaseManagerView({
        viewModel:{
            loading: loading
        }
    });
});
