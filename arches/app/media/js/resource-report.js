require([
    'jquery',
    'arches',
    "bootstrap"
], function($, arches) {
    $(document).ready(function() {
        require(['views/reports/' + $('#report-id').val()], function (ReportView) {
            if (ReportView) {
                var reportView = new ReportView({
                    el: $('#resource_report')[0]
                });
            }
        });
    });
});
