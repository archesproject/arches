require([
    'knockout',
    'views/graph/graph-page-view',
    'views/graph/card-configuration/card-component-form',
    'views/graph/card-configuration/card-components-tree',
    'views/graph/card-configuration/card-form-preview',
    'card-configuration-data'
], function(ko, PageView, CardComponentForm, CardComponentsTree, CardFormPreview, data) {
    /**
    * set up the page view model with the related sub views
    */
    var viewModel = {
        cardComponentForm: new CardComponentForm(),
        cardComponentsTree: new CardComponentsTree(),
        cardFormPreview: new CardFormPreview()
    };

    var pageView = new PageView({
        viewModel: viewModel
    });
});
