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

    var formModel = new FormModel({
        data: data.form,
        forms_x_cards: data.forms_x_cards,
        cards: data.cards
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
            items: formModel.availableCards
        }),
        addedCards: formModel.cards,
        selectedFormId: ko.observable(data.form.formid),
        openForm: function (formId) {
            pageView.viewModel.navigate(arches.urls.form_configuration + formId);
        },
        addCard: function(card) {
            formModel.availableCards.remove(card);
            formModel.cards.push(card);
        },
        removeCard: function(card) {
            formModel.cards.remove(card);
            formModel.availableCards.push(card);
        },
        save: function () {

        },
        cancel: function () {
            formModel.reset();
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
