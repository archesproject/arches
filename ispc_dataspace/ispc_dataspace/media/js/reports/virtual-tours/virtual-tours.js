define([
    'underscore',
    'knockout',
    'viewmodels/report',
    'reports/virtual-tours/virtual-tours-setup',
    'arches',
    'knockstrap',
    'bindings/chosen',
],
function (_, ko, ReportViewModel, virtualToursSetup ,arches) {
    return ko.components.register('virtual-tours-report', {
        viewModel: function (params) {
            var self = this;
            params.configKeys = ['nodes'];
            ReportViewModel.apply(this, [params]);

            self.virtualTourZipFiles = ko.observableArray([]);

            if (self.report.get('tiles')) {
                var virtualTourZipFiles = [];
                self.report.get('tiles').forEach(function (tile) {
                    _.each(tile.data, function (val) {
                        if (Array.isArray(val)) {
                            val.forEach(function (item) {

                                if (item.status &&
                                    (item.name.split('.').pop() == 'zip')) {
                                        // Hotfix for status being 'queued' while the file is actually uploaded
                                        if (item.status == 'queued'){
                                            let url = arches.urls.uploadedfiles + item.name;
                                            console.log("setting url: " + url);
                                            item.url = url;
                                        }
                                    virtualTourZipFiles.push({
                                        src: item.url,
                                        name: item.name
                                    });
                                }
                            });
                        }
                    }, self);
                }, self);

                if (virtualTourZipFiles.length > 0) {
                    self.virtualTourZipFiles(virtualTourZipFiles);
                    let filepath = virtualTourZipFiles[0].src;
                    let originalName = virtualTourZipFiles[0].name;

                    let filepathWithoutExtension = "";
                    if (filepath != null) {
                        filepathWithoutExtension = filepath.replace(/\.[^/.]+$/, "");
                    }

                    let originalNameWithoutExtension = ""
                    if (originalName != null) {
                        originalNameWithoutExtension = originalName.replace(/\.[^/.]+$/, "");
                    }

                    let htmlPath = filepathWithoutExtension + '/' + originalNameWithoutExtension + '/' + originalNameWithoutExtension + '.html';
                    virtualToursSetup.setupVirtualTours(htmlPath)
                }
            }

            var widgets = [];
            var getCardWidgets = function (card) {
                widgets = widgets.concat(card.model.get('widgets')());
                card.cards().forEach(function (card) {
                    getCardWidgets(card);
                });
            };
            ko.unwrap(self.report.cards).forEach(getCardWidgets);

            this.nodeOptions = ko.observableArray(
                widgets.map(function (widget) {
                    return widget.node
                }).filter(function (node) {
                    return ko.unwrap(node.datatype) === 'file-list';
                })
            );
        },
        template: {
            require: 'text!report-templates/virtual-tours'
        }
    });
});