
require([
    'knockout',
    'models/card',
    'views/graph/graph-page-view',
    'views/graph/card-configuration/card-component-form',
    'views/graph/card-configuration/card-components-tree',
    'views/graph/card-configuration/card-form-preview',
    'card-configuration-data',
    'datatype-config-components'
], function(ko, CardModel, PageView, CardComponentForm, CardComponentsTree, CardFormPreview, data) {
    var viewModel = {
        card: new CardModel({
            data: data.card,
            datatypes: data.datatypes
        }),
        permissions: data.permissions,
        functions: data.functions,
        helpPreviewActive: ko.observable(false)
    };
    viewModel.dirty = viewModel.card.dirty;
    viewModel.selection = ko.observable(viewModel.card);

    viewModel.cardComponentsTree = new CardComponentsTree(viewModel);

    viewModel.cardComponentForm = new CardComponentForm(viewModel);

    viewModel.cardFormPreview = new CardFormPreview(viewModel);

    var pageView = new PageView({viewModel: viewModel});
});
