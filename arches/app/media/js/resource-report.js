require([
    'jquery',
    'arches',
    'bootstrap',
    'plugins/circles-master/circles',
    'plugins/circles-master',
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
