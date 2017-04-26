define(['jquery', 'knockout', 'arches', 'bindings/smartresize'], function ($, ko, arches) {
    /**
    * A base viewmodel for functions
    *
    * @constructor
    * @name SavedSearchesViewModel
    *
    * @param  {string} params - a configuration object
    */
    var SavedSearchesViewModel = function(params) {
        var self = this;
        var mediaUrl = arches.urls.uploadedfiles;
        self.items = ko.observableArray([
            {image: mediaUrl + 'uploadedfiles/q9.jpg', title:'Prehistoric Archaeological Sites', subtitle: 'Paleolithic remains and finds!', search: ''},
            {image: mediaUrl + 'uploadedfiles/q8.jpg', title:'In the Shadow of the Volcano ', subtitle:'Resources at risk of volcanic eruptions',  search: ''},
            {image: mediaUrl + 'uploadedfiles/q7.jpg', title:'Canal District', subtitle: 'Designated buildings and structures in Venice', search: ''},
            {image: mediaUrl + 'uploadedfiles/q6.jpg', title:'San Francisco Heritage Resources', subtitle: 'Important Heritage in the heart of California', search: ''},
            {image: mediaUrl + 'uploadedfiles/q5.jpg', title:'Query 5 Name', subtitle: 'Query 5 subtitle', search: ''},
            {image: mediaUrl + 'uploadedfiles/q4.jpg', title:'Query 6 Name', subtitle: 'Query 6 subtitle', search: ''},
        ]);
        self.options = {
            itemSelector: '.ss-grid-item',
            masonry: {
                columnWidth: 500,
                gutterWidth: 25,
            }
        };
    };
    return SavedSearchesViewModel;
});
