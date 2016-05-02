require([
    'underscore',
    'knockout',
    'views/page-view'
], function(_, ko, PageView) {
    var icons = JSON.parse($('#icon-data').val());
    var iconFilter = ko.observable('');
    var selectedIconClass = ko.observable('');
    var viewModel = {
        iconFilter: iconFilter,
        icons: ko.computed(function () {
            return _.filter(icons, function (icon) {
                return icon.name.indexOf(iconFilter()) >= 0;
            });
        }),
        selectedIconClass: selectedIconClass
    };

    new PageView({
        viewModel: viewModel
    });
});
