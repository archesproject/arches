define([
    'jquery',
    'knockout',
    'arches',
    'templates/views/components/search/saved-searches.htm',
    'bindings/smartresize',
], function($, ko, arches, savedSearchesTemplate) {
    var componentName = 'saved-searches';
    const viewModel = function(params) {
        var self = this;
        self.items = ko.observableArray([]);
        $.ajax({
            type: "GET",
            url: arches.urls.api_search_component_data + componentName,
            context: this
        }).done(function(response) {
            response.saved_searches.forEach(function(search) {
                var searchImageUrl = arches.urls.url_subpath + ((search.IMAGE && search.IMAGE.length > 0) ? search.IMAGE[0].url : '');
                searchImageUrl = searchImageUrl.replace('//', '/');
                self.items.push({
                    image: searchImageUrl,
                    title: search.SEARCH_NAME,
                    subtitle: search.SEARCH_DESCRIPTION,
                    searchUrl: search.SEARCH_URL
                });
            });
        });

        self.options = {
            itemSelector: '.ss-grid-item',
            masonry: {
                columnWidth: 500,
                gutterWidth: 25,
            }
        };
    };

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: savedSearchesTemplate,
    });
});
