require([
    'knockout',
    'models/card',
    'models/graph',
    'views/graph/graph-page-view',
    'views/graph/card-configuration/card-component-form',
    'views/graph/card-configuration/card-components-tree',
    'views/graph/card-configuration/card-form-preview',
    'card-configuration-data',
    'arches',
    'datatype-config-components'
], function(ko, CardModel, GraphModel, PageView, CardComponentForm, CardComponentsTree, CardFormPreview, data, arches) {
    var options = [{
        name: null,
        graphId: null,
        disabled: true
    }];
    var viewModel = {
        card: new CardModel({
            data: data.card,
            datatypes: data.datatypes
        }),
        graphModel: new GraphModel({
            data: data.graph
        }),
        ontology_properties: data.ontology_properties,
        helpPreviewActive: ko.observable(false),
        reset: function () {
            viewModel.card.reset();
            viewModel.selection(viewModel.card);
        },
        save: function () {
            pageView.viewModel.loading(true);
            viewModel.card.save(function(request, status, self){
                pageView.viewModel.loading(false);
                if(status !== 'success'){
                    pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
                } else {
                    viewModel.graphCardOptions(options.concat(graphCards));
                }
            });
        },
        selectedCardId: ko.observable(data.card.cardid)
    };
    viewModel.dirty = viewModel.card.dirty;
    viewModel.selection = ko.observable(viewModel.card);
    var graphCards = viewModel.graphModel.graphCards();
    _.each(graphCards, function (card) {
        if (card.cardid === data.card.cardid) {
            card.name = viewModel.card.get('name');
        } else {
            card.name = ko.observable(card.name);
        }
    });

    viewModel.graphCardOptions = ko.observableArray(options.concat(graphCards));

    viewModel.openCard = function (cardId) {
        pageView.viewModel.navigate(arches.urls.card + cardId);
    };

    viewModel.selectedCardId.subscribe(function(cardId) {
        if (cardId) {
            viewModel.openCard(cardId);
        }
    });

    viewModel.cardComponentsTree = new CardComponentsTree(viewModel);

    viewModel.cardComponentForm = new CardComponentForm(viewModel);

    viewModel.cardFormPreview = new CardFormPreview(viewModel);

    var pageView = new PageView({viewModel: viewModel});
});
