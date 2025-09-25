import _ from 'underscore';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import arches from 'arches';
import ReportViewModel from 'viewmodels/report';
import imageReportTemplate from 'templates/views/report-templates/image.htm';

import 'knockstrap';
import 'bindings/chosen';

export default ko.components.register('image-report', {
    viewModel: function (params) {
        var self = this;
        params.configKeys = ['nodes'];

        ReportViewModel.apply(this, [params]);

        self.imgs = ko.computed(function () {
            var imgs = [];
            var nodes = ko.unwrap(self.nodes);
            self.tiles().forEach(function (tile) {
                _.each(tile.data, function (val, key) {
                    val = koMapping.toJS(val);
                    if (Array.isArray(val)) {
                        val.forEach(function (item) {
                            if (item.status &&
                                item.type &&
                                item.status === 'uploaded' &&
                                item.type.indexOf('image') > -1 &&
                                _.contains(nodes, key)
                            ) {
                                imgs.push({
                                    src: (arches.urls.url_subpath + ko.unwrap(item.url)).replace('//', '/'),
                                    alt: item.name
                                });
                            }
                        });
                    }
                }, self);
            }, self);
            if (imgs.length === 0) {
                imgs = [{
                    src: arches.urls.media + 'img/photo_missing.png',
                    alt: arches.translations.imageNotAvailable,
                }];
            }
            return imgs;
        });

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
                return widget.node;
            }).filter(function (node) {
                return ko.unwrap(node.datatype) === 'file-list';
            })
        );
    },
    template: imageReportTemplate,
});
