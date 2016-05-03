require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/page-view'
], function($, _, ko, koMapping, PageView) {
    var icons = JSON.parse($('#icon-data').val());
    var srcJSON = $('#graph-metadata').val();
    var metadata = koMapping.fromJSON(srcJSON);
    var iconFilter = ko.observable('');
    var viewModel = {
        iconFilter: iconFilter,
        icons: ko.computed(function () {
            return _.filter(icons, function (icon) {
                return icon.name.indexOf(iconFilter()) >= 0;
            });
        }),
        metadata: metadata,
        save: function () {
            pageView.viewModel.loading(true);
            $.ajax({
                type: "POST",
                url: '',
                data: koMapping.toJSON(metadata),
                success: function(response) {
                    pageView.viewModel.loading(false);
                },
                failure: function(response) {
                    pageView.viewModel.loading(false);
                }
            });
        },
        reset: function () {
            _.each(JSON.parse(srcJSON), function(value, key) {
                metadata[key](value);
            });
        }
    };

    var pageView = new PageView({
        viewModel: viewModel
    });
});
