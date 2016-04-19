require([
    'jquery',
    'views/page-view',
    'bootstrap-nifty'
], function($, PageView) {
    var resources = JSON.parse($('#resources').val());
    new PageView({
        viewModel: {
            resources: resources
        }
    });
});
