
define(['knockout', 'views/list', 'bindings/chosen'], function(ko, ListView, chosen) {
    /**
     * A viewmodel used for a related resources list
     *
     * @constructor
     * @name RelatedResourcesListViewModel
     *
     */
    var RelatedResourcesList = function(params) {
        var self = this;
        this.relationships = params.relationships;
        this.relatedList = new ListView({
            items: this.relationships
        });
    };
    return RelatedResourcesList;
});
