require([
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/page-view'
], function(_, ko, koMapping, PageView) {
    var icons = JSON.parse($('#icon-data').val());
    var node = koMapping.fromJSON($('#node-data').val());
    var metadata = koMapping.fromJSON($('#graph-metadata').val());
    var iconFilter = ko.observable('');
    var selectedIconClass = ko.observable('');
    var viewModel = {
        iconFilter: iconFilter,
        icons: ko.computed(function () {
            return _.filter(icons, function (icon) {
                return icon.name.indexOf(iconFilter()) >= 0;
            });
        }),
        selectedIconClass: selectedIconClass,
        node: node,
        metadata: metadata
    };

    new PageView({
        viewModel: viewModel
    });
});
