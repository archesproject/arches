require([
    'jquery',
    'underscore',
    'views/page-view',
    'bootstrap-nifty'
], function($, _, PageView) {
    var resources = JSON.parse($('#resources').val());
    var branches = JSON.parse($('#branches').val());
    resources.forEach(function(resource) {
        resource.branch = _.find(branches, function(branch) {
            return branch.branchmetadataid === resource.branchmetadata_id;
        });
        resource.open = function() {
            window.location = resource.nodeid;
        }
    });
    new PageView({
        viewModel: {
            resources: resources
        }
    });
});
