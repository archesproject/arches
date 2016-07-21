require([
    'knockout',
    'models/card',
    'views/graph/graph-page-view',
    'views/graph/card-configuration/card-component-form',
    'views/graph/card-configuration/card-components-tree',
    'views/graph/card-configuration/card-form-preview',
    'card-configuration-data'
], function(ko, CardModel, PageView, CardComponentForm, CardComponentsTree, CardFormPreview, data) {
    /**
    * set up the page view model with the related sub views
    */
    data.card.cards = data.subCards;
    var setupCard = function (card) {
        card.nodegroup = data.nodeGroups.find(function (nodegroup) {
            return nodegroup.nodegroupid === card.nodegroup_id;
        });
        card.nodes = data.nodes.filter(function (node) {
            return node.nodegroup_id === card.nodegroup_id;
        });
        if (card.cards) {
            card.cards.forEach(function(card) {
                setupCard(card);
            });
        } else {
            card.cards = [];
        }
    };
    setupCard(data.card);

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
