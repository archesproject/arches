define(['jquery',
    'knockout',
    'arches',
    'search-data',
    'bindings/smartresize'],
function($, ko, arches, data) {
    return ko.components.register('saved-searches', {
        viewModel: function(params) {
            var self = this;
            var mediaUrl = arches.urls.uploadedfiles;
            self.items = ko.observableArray([]);
            data.saved_searches.forEach(function(search) {
                var searchImageUrl = (search.IMAGE && search.IMAGE.length > 0) ? search.IMAGE[0].url : '';
                self.items.push({
                    image: searchImageUrl,
                    title: search.SEARCH_NAME,
                    subtitle: search.SEARCH_DESCRIPTION,
                    searchUrl: search.SEARCH_URL
                });
            });

            self.options = {
                itemSelector: '.ss-grid-item',
                masonry: {
                    columnWidth: 500,
                    gutterWidth: 25,
                }
            };
        },
        template: { require: 'text!templates/views/components/search/saved-searches.htm'}
    });
});
