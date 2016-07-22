require([
    'knockout',
    'models/card',
    'views/graph/graph-page-view',
    'views/graph/card-configuration/card-component-form',
    'views/graph/card-configuration/card-components-tree',
    'views/graph/card-configuration/card-form-preview',
    'card-configuration-data'
], function(ko, CardModel, PageView, CardComponentForm, CardComponentsTree, CardFormPreview, data) {
    var viewModel = {};

    var cardModel = new CardModel({
        data: data.card,
        datatypes: data.datatypes
    });

    viewModel.cardComponentsTree = new CardComponentsTree({
        card: cardModel
    });

    // global observable for selected component
    viewModel.selection = viewModel.cardComponentsTree.selection;

    viewModel.cardComponentForm = new CardComponentForm({
        card: cardModel
    });

    viewModel.cardFormPreview = new CardFormPreview({
        card: cardModel
    });

    var pageView = new PageView({
        viewModel: viewModel
    });
});
