define([
    'underscore',
    'knockout',
    'viewmodels/report',
    'plugins/knockstrap',
    'bindings/chosen'
], function(_, ko, ReportViewModel) {
    return ko.components.register('image-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['nodes'];

            ReportViewModel.apply(this, [params]);
            self.imgs = ko.observableArray([{
                src: '/media/img/photo_missing.png',
                alt: ''
            }]);

            if (self.report.get('tiles')) {
                var imgs = [];
                var nodes = self.nodes();
                self.report.get('tiles').forEach(function(tile) {
                    _.each(tile.data, function(val, key) {
                        if (Array.isArray(val)) {
                            val.forEach(function(item) {
                                if (item.status &&
                                    item.type &&
                                    item.status === 'uploaded' &&
                                    item.type.indexOf('image') > -1 &&
                                    _.contains(nodes, key)
                                ) {
                                    imgs.push({
                                        src: item.url,
                                        alt: item.name
                                    });
                                }
                            });
                        }
                    }, self);
                }, self);
                if (imgs.length > 0) {
                    self.imgs(imgs);
                }
            }
            var widgets = [];
            self.report.forms().forEach(function (form) {
                form.cards.forEach(function(card) {
                    widgets = widgets.concat(card.get('widgets')());
                    card.get('cards')().forEach(function(card) {
                        widgets = widgets.concat(card.get('widgets')());
                    });
                });
            });
            this.nodeOptions = ko.observableArray(
                widgets.map(function(widget) {
                    return widget.node
                }).filter(function (node) {
                    return ko.unwrap(node.datatype) === 'file-list';
                })
            );
        },
        template: {
            require: 'text!report-templates/image'
        }
    });
});
