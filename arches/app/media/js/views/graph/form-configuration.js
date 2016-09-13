require([
    'knockout',
    'arches',
    'models/graph',
    'models/form',
    'views/graph/form-settings',
    'views/graph/graph-page-view',
    'views/list',
    'form-configuration-data',
    'bindings/sortable'
], function(ko, arches, GraphModel, FormModel, FormSettingsView, PageView, ListView, data) {
    /**
    * a PageView representing the form configuration page
    */
    var self = this;
    var options = [{
        title: null,
        formid: null,
        disabled: true
    }];

    var formModel = new FormModel({data:data.form});
    var addedCards = ko.observableArray(_.map(data.forms_x_cards, function (formXCard) {
        return _.find(data.cards, function(card) {
            return card.cardid === formXCard.card_id;
        });
    }));
    var availableCards = ko.observableArray();
    var addedCardIds = _.map(data.forms_x_cards, function (formXCard) {
        return formXCard.card_id;
    });
    _.each(data.cards, function (card) {
        if (!_.contains(addedCardIds, card.cardid)) {
            availableCards.push(card);
        }
    });

    var viewModel = {
        dirty: formModel.dirty,
        formOptions: options.concat(data.forms),
        formSettings: new FormSettingsView({
            formModel: formModel,
            icons: data.icons
        }),
        graphModel: new GraphModel({
            data: data.graph
        }),

        cardList: new ListView({
            items: availableCards
        }),
        addedCards: addedCards,
        selectedFormId: ko.observable(data.form.formid),
        openForm: function (formId) {
            pageView.viewModel.navigate(arches.urls.form_configuration + formId);
        },
        addCard: function(card) {
            availableCards.remove(card);
            addedCards.push(card);
        },
        removeCard: function(card) {
            addedCards.remove(card);
            availableCards.push(card);
        }
    };

    var pageView = new PageView({
        viewModel: viewModel
    });

    pageView.viewModel.selectedFormId.subscribe(function(formId) {
        if (formId) {
            pageView.viewModel.openForm(formId);
        }
    });
});
