define([
    'arches',
    'viewmodels/remote-domain-widget',
], function(arches, RemoteDomainWidgetViewModel) {
    /**
    * A viewmodel used for concept widgets
    *
    * @constructor
    * @name ConceptWidgetViewModel
    *
    * @param  {string} params - a configuration object
    */

    var ConceptWidgetViewModel = function(params) {
        var self = this;

        params.prepData = function(data) {
            data.forEach(function(record) {
                if (record.collector) {
                    record.id = undefined;
                }
            });
            return data;
        };

        RemoteDomainWidgetViewModel.apply(this, [params]);

        var setUrl = function(id) {
            if (id) {
                self.url(arches.urls.dropdown + '?conceptid=' + id);
            }
        };

        this.node.config.rdmCollection.subscribe(setUrl);
        setUrl(this.node.config.rdmCollection());
    };

    return ConceptWidgetViewModel;
});
