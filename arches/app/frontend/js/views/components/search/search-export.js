define(['jquery',
    'knockout',
    'arches',
    'bindings/fadeVisible',
    'bindings/clipboard',
    'views/components/simple-switch'],
function($, ko, arches) {
    var componentName = 'search-export';
    return ko.components.register(componentName, {
        viewModel: function(params) {
            var self = this;
            this.total = params.total;
            this.query = params.query;
            this.downloadStarted = ko.observable(false);
            this.reportlink = ko.observable(false);
            this.format = ko.observable('tilecsv');
            this.precision = ko.observable(6);
            this.result = ko.observable();
            this.emailInput = ko.observable(arches.userEmail);
            this.exportName = ko.observable();
            this.celeryRunning = ko.observable(arches.celeryRunning);
            this.hasExportHtmlTemplates = ko.observable(arches.exportHtmlTemplates.length > 0);
            this.downloadPending = ko.observable(false);
            this.hasResourceTypeFilter = ko.observable(!!params.query()['resource-type-filter']);

            this.query.subscribe(function(val) {
                if (val['resource-type-filter']) {
                    self.hasResourceTypeFilter(true);
                }
                else {
                    self.hasResourceTypeFilter(false);
                }
            });

            this.hasResourceTypeFilter.subscribe(function(val) {
                if (!val) {
                    self.format('tilecsv');
                }
            });

            this.url = ko.computed(function() {
                var url = arches.urls.export_results;
                var urlparams = ko.unwrap(self.query);
                urlparams.format = self.format();
                urlparams.reportlink = self.reportlink();
                urlparams.precision = self.precision();
                urlparams.total = self.total();
                url = url + '?' + $.param(urlparams);
                return url;
            });

            this.geojsonUrl = ko.pureComputed(function(){
                if (ko.unwrap(self.format()) === 'geojson') {
                    var exportPath = self.url().replace('search/export_results', 'api/search/export_results');
                    return window.location.origin + exportPath;
                } else {
                    return null;
                }
            });

            this.getExportData = function(){
                var payload = ko.unwrap(this.query);
                self.downloadPending(true);
                payload.format = this.format();
                payload.reportlink = this.reportlink();
                payload.precision = this.precision();
                payload.total = this.total();
                payload.email = this.emailInput();
                payload.exportName = this.exportName() || "Arches Export";
                $.ajax({
                    type: "GET",
                    url: arches.urls.export_results,
                    data: payload
                }).done(function(response) {
                    self.downloadPending(false);
                    self.downloadStarted(true);
                    window.setTimeout(function(){
                        self.downloadStarted(false);
                    }, 9000);
                    self.result(response.message);
                });
            };

            this.executeExport = function(limit){
                if (ko.unwrap(self.format()) === 'geojson' && this.total() <= limit) {
                    window.open(this.geojsonUrl());
                } else if (this.total() > limit) {
                    this.getExportData();
                } else if (this.total() > 0) {
                    window.open(this.url());
                }
            };

        },
        template: { require: 'text!templates/views/components/search/search-export.htm'}
    });
});
