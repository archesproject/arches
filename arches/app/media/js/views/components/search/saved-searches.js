import $ from 'jquery';
import ko from 'knockout';
import arches from 'arches';
import savedSearchesTemplate from 'templates/views/components/search/saved-searches.htm';
import 'bindings/smartresize';


const componentName = 'saved-searches';
const viewModel = function(params) {
    var self = this;
    self.searchFilterVms = params.searchFilterVms;

        
    self.urls = arches.urls;
    self.selectedPopup = params.selectedPopup;
    self.items = ko.observableArray([]);
    $.ajax({
        type: "GET",
        url: arches.urls.api_search_component_data + componentName,
        context: this
    }).done(function(response) {
        response[componentName].forEach(function(search) {
            let searchImageUrl = arches.urls.url_subpath + ((search.IMAGE && search.IMAGE.length > 0) ? search.IMAGE[0].url : '');
            searchImageUrl = searchImageUrl.replace('//', '/');
            self.items.push({
                image: searchImageUrl,
                title: search.SEARCH_NAME ? search.SEARCH_NAME[arches.activeLanguage].value : "",
                subtitle: search.SEARCH_DESCRIPTION ? search.SEARCH_DESCRIPTION[arches.activeLanguage].value : "",
                searchUrl: search.SEARCH_URL ? search.SEARCH_URL[arches.activeLanguage].value: ""
            });
        });
        self.searchFilterVms[componentName](self);
    });

    self.options = {
        itemSelector: '.ss-grid-item',
        masonry: {
            columnWidth: 500,
            gutterWidth: 25,
        }
    };
};

export default ko.components.register(componentName, {
    viewModel: viewModel,
    template: savedSearchesTemplate,
});
