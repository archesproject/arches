require([
    'underscore',
    'knockout',
    'arches',
    'models/graph',
    'models/form',
    'views/graph/form-settings',
    'views/graph/graph-page-view',
    'views/list',
    'viewmodels/alert',
    'form-configuration-data',
    'bindings/sortable'
], function(_, ko, arches, GraphModel, FormModel, FormSettingsView, PageView, ListView, AlertViewModel, data) {
    /**
    * a PageView representing the form configuration page
    */
    var self = this;
    var options = [{
        title: ko.observable(null),
        formid: null,
        disabled: true
    }];

    var formModel = new FormModel({
        data: data.form,
        forms_x_cards: data.forms_x_cards,
        cards: data.cards
    });
    _.each(data.forms, function (form) {
        if (form.formid === formModel.formid) {
            form.title = formModel.title;
        } else {
            form.title = ko.observable(form.title);
        }
    });

    var viewModel = {
        dirty: formModel.dirty,
        formOptions: ko.observableArray(options.concat(data.forms)),
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
        openForm: function (formId, bypass) {
            pageView.viewModel.navigate(arches.urls.form + formId, bypass);
        },
        addForm: function (bypass) {
            if (!bypass && pageView.viewModel.dirty()) {
                pageView.viewModel.alert(new AlertViewModel('ep-alert-blue', arches.confirmNav.title, arches.confirmNav.text, function(){
                    pageView.viewModel.showConfirmNav(false);
                }, function() {
                    pageView.viewModel.addForm(true);
                }));
                return;
            }
            pageView.viewModel.alert(null)
            pageView.viewModel.loading(true);
            $.ajax({
                type: "POST",
                url: '../graph/' + data.graph.graphid + '/add_form',
                success: function(response) {
                    pageView.viewModel.openForm(response.formid, true);
                },
                error: function(response) {
                    pageView.viewModel.loading(false);
                    pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
                }
            });
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
            pageView.viewModel.loading(true);
            formModel.save(function(request, status, self){
                pageView.viewModel.loading(false);
                if(status !== 'success'){
                    pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
                } else {
                    formModel.parse(JSON.parse(request.responseText));
                    viewModel.formOptions(options.concat(data.forms));
                }
            });
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
