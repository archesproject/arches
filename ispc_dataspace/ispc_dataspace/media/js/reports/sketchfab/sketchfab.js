define([
    'underscore',
    'knockout',
    'viewmodels/report',
    'reports/sketchfab/sketchfab-setup',
    'arches',
    'knockstrap',
    'bindings/chosen',
],
function (_, ko, ReportViewModel, sketchfabSetup, arches) {
    return ko.components.register('sketchfab-report', {
        viewModel: function (params) {
            var self = this;
            params.configKeys = ['nodes'];
            ReportViewModel.apply(this, [params]);

            self.sketchfabUrl = ko.observable();

            if (self.report.get('tiles')) {
                let sketchfabUrl;
                self.report.get('tiles').forEach(function (tile) {
                    if (tile.nodegroup_id == '6ba5bf96-f58b-11e8-a354-0242ac120004'){
                        if ('6ba5c75c-f58b-11e8-a354-0242ac120004' in tile.data){
                            sketchfabUrl = tile.data['6ba5c75c-f58b-11e8-a354-0242ac120004'];
                        }
                    }
                }, self);

                if (sketchfabUrl) {
                    self.sketchfabUrl(sketchfabUrl);
                    let embedUrl = sketchfabUrl + '/embed'

                    sketchfabSetup.setupSketchfab(embedUrl)
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
            require: 'text!report-templates/sketchfab'
        }
    });
});