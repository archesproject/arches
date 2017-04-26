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
            {image: mediaUrl + 'uploadedfiles/q9.jpg', title:'Prehistoric Archaeological Sites', subtitle: 'Paleolithic remains and finds!', searchUrl: 'search?termFilter=%5B%7B%22inverted%22%3Afalse%2C%22type%22%3A%22string%22%2C%22context%22%3A%22%22%2C%22context_label%22%3A%22%22%2C%22id%22%3A%22Prehistoric%22%2C%22text%22%3A%22Prehistoric%22%2C%22value%22%3A%22Prehistoric%22%7D%5D&no_filters=false&page=1'},
            {image: mediaUrl + 'uploadedfiles/q8.jpg', title:'In the Shadow of the Volcano ', subtitle:'Resources at risk of volcanic eruptions',  searchUrl: 'search?termFilter=%5B%7B"text"%3A"The%20Geology%20of%20Lincolnshire"%2C"value"%3A"The%20Geology%20of%20Lincolnshire"%2C"context"%3A""%2C"context_label"%3A""%2C"type"%3A"term"%2C"id"%3A2%2C"inverted"%3Afalse%7D%5D&no_filters=false&page=1'},
            {image: mediaUrl + 'uploadedfiles/q7.jpg', title:'Canal District', subtitle: 'Designated buildings and structures in Venice', searchUrl: 'search?termFilter=%5B%7B"inverted"%3Afalse%2C"type"%3A"string"%2C"context"%3A""%2C"context_label"%3A""%2C"id"%3A"canal"%2C"text"%3A"canal"%2C"value"%3A"canal"%7D%5D&no_filters=false&page=1'},
            {image: mediaUrl + 'uploadedfiles/q6.jpg', title:'San Francisco Heritage Resources', subtitle: 'Important Heritage in the heart of California', searchUrl: 'search?termFilter=%5B%7B%22inverted%22%3Afalse%2C%22type%22%3A%22string%22%2C%22context%22%3A%22%22%2C%22context_label%22%3A%22%22%2C%22id%22%3A%22Heritage%22%2C%22text%22%3A%22Heritage%22%2C%22value%22%3A%22Heritage%22%7D%5D&no_filters=false&page=1'},
            {image: mediaUrl + 'uploadedfiles/q5.jpg', title:'Query 5 Name', subtitle: 'Query 5 subtitle', searchUrl: 'search?termFilter=%5B%7B%22inverted%22%3Afalse%2C%22type%22%3A%22string%22%2C%22context%22%3A%22%22%2C%22context_label%22%3A%22%22%2C%22id%22%3A%22Lincoln%22%2C%22text%22%3A%22Lincoln%22%2C%22value%22%3A%22Lincoln%22%7D%5D&no_filters=false&page=1'},
            {image: mediaUrl + 'uploadedfiles/q4.jpg', title:'Query 6 Name', subtitle: 'Query 6 subtitle', searchUrl: 'search?termFilter=%5B%7B%22inverted%22%3Afalse%2C%22type%22%3A%22string%22%2C%22context%22%3A%22%22%2C%22context_label%22%3A%22%22%2C%22id%22%3A%22Quorn%22%2C%22text%22%3A%22Quorn%22%2C%22value%22%3A%22Quorn%22%7D%5D&no_filters=false&page=1'}
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
