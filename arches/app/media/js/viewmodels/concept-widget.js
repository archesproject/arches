define([
    'viewmodels/remote-domain-widget',
    'arches'
], function (RemoteDomainWidgetViewModel, arches) {
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

        RemoteDomainWidgetViewModel.apply(this, [params]);

        var setUrl = function (id) {
            if (id) {
                self.url(arches.urls.dropdown + '?conceptid=' + id)
            }
        };

        this.node.config.topConcept.subscribe(setUrl);
        setUrl(this.node.config.topConcept());
    };

    return ConceptWidgetViewModel;
});
