require(['jquery', 'backbone','arches', 'views/resource-search'], function($, Backbone, arches, ResourceSearch) {
    $(document).ready(function() {
        var searchbox = new ResourceSearch({
            el: $.find('input.resource_search_widget')[0]
        })
       
    });
});