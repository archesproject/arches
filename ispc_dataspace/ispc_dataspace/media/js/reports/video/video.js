define([
    'underscore',
    'knockout',
    'viewmodels/report',
    'reports/video/video-setup',
    'arches',
    'knockstrap',
    'bindings/chosen',
],
function (_, ko, ReportViewModel, videoSetup, arches) {
    return ko.components.register('video-report', {
        viewModel: function (params) {
            var self = this;
            params.configKeys = ['nodes'];
            ReportViewModel.apply(this, [params]);

            self.videoUrl = ko.observable();

            if (self.report.get('tiles')) {
                let videoUrl;
                let videoPlayerType;
                self.report.get('tiles').forEach(function (tile) {
                    if (tile.nodegroup_id == '32a84ee6-f60f-11e8-8d50-0242ac120004'){
                        if ('32a86f84-f60f-11e8-8d50-0242ac120004' in tile.data){
                            videoUrl = tile.data['32a86f84-f60f-11e8-8d50-0242ac120004'];
                        }
                        if ('23e11bb0-f612-11e8-bcc8-0242ac120004' in tile.data){
                            let videoPlayerTypeConcept = tile.data['23e11bb0-f612-11e8-bcc8-0242ac120004'];
                            if (videoPlayerTypeConcept == 'b43c2210-881f-4c1b-ac9b-7d24e72413fe'){
                                videoPlayerType = 'YouTube';
                            }
                        }

                    }
                }, self);

                if (videoUrl) {
                    videoSetup.setupVideo(videoUrl, videoPlayerType)
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
            require: 'text!report-templates/video'
        }
    });
});