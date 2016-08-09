require([
    'knockout',
    'models/card',
    'views/graph/graph-page-view',
    'views/graph/card-configuration/card-component-form',
    'views/graph/card-configuration/card-components-tree',
    'views/graph/card-configuration/card-form-preview',
    'card-configuration-data',
    'widgets/switch'
], function(ko, CardModel, PageView, CardComponentForm, CardComponentsTree, CardFormPreview, data) {
    var viewModel = {};

    var cardModel = new CardModel({
        data: data.card,
        datatypes: data.datatypes
    });

    viewModel.card = cardModel;

    viewModel.cardComponentsTree = new CardComponentsTree({
        card: cardModel
    });

    var selection = viewModel.cardComponentsTree.selection;
    viewModel.cardComponentForm = new CardComponentForm({
        card: cardModel,
        selection: selection
    });

    var helpPreviewActive = viewModel.cardComponentForm.helpPreviewActive;
    viewModel.cardFormPreview = new CardFormPreview({
        card: cardModel,
        selection: selection,
        helpPreviewActive: helpPreviewActive
    });

    var pageView = new PageView({
        viewModel: viewModel
    });
});
