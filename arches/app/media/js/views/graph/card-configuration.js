require([
    'knockout',
    'models/card',
    'views/graph/graph-page-view',
    'views/graph/card-configuration/card-component-form',
    'views/graph/card-configuration/card-components-tree',
    'views/graph/card-configuration/card-form-preview',
    'card-configuration-data'
], function(ko, CardModel, PageView, CardComponentForm, CardComponentsTree, CardFormPreview, data) {

    var cardModel = new CardModel({
        data: data.card,
        datatypes: data.datatypes
    });
    
    var viewModel = {
        cardComponentForm: new CardComponentForm(),
        cardComponentsTree: new CardComponentsTree({
            card: cardModel
        }),
        cardFormPreview: new CardFormPreview()
    };

    var pageView = new PageView({
        viewModel: viewModel
    });
});
