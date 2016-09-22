require([
    'jquery',
    'underscore',
    'knockout',
    'models/graph',
    'views/graph/graph-page-view',
    'viewmodels/alert',
    'arches',
    'graph-forms-data',
    'bindings/sortable'
], function($, _, ko, GraphModel, PageView, AlertViewModel, arches, data) {

    /**
    * a PageView representing the graph forms page
    */
    var self = this;

    _.each(data.forms, function(form) {
        form.cards = [];
        _.each(data.forms_x_cards, function (form_x_card) {
            if (form_x_card.form_id !== form.formid) {
                return;
            }
            var card = _.find(data.cards, function (card) {
                return card.cardid === form_x_card.card_id;
            });
            form.cards.push(card);
        });
    });

    var options = [{
        title: null,
        formid: null,
        disabled: true
    }];

    var viewModel = {
        graphModel: new GraphModel({
            data: data.graph
        }),
        forms: ko.observableArray(data.forms),
        formOptions: options.concat(data.forms),
        openForm: function (formId) {
            pageView.viewModel.navigate(arches.urls.form + formId);
        },
        addForm: function () {
            pageView.viewModel.loading(true);
            $.ajax({
                type: "POST",
                url: 'add_form',
                success: function(response) {
                    pageView.viewModel.openForm(response.formid);
                },
                error: function(response) {
                    pageView.viewModel.loading(false);
                    pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
                }
            });
        },
        reorderForms: function () {
            pageView.viewModel.loading(true);
            $.ajax({
                type: "POST",
                data: JSON.stringify({
                    forms: viewModel.forms()
                }),
                url: 'reorder_forms',
                success: function(response) {
                    pageView.viewModel.loading(false);
                },
                error: function(response) {
                    pageView.viewModel.loading(false);
                    pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
                }
            });
        },
        deleteForm: function (form) {
            $.ajax({
                type: "DELETE",
                url: arches.urls.form + form.formid + '/delete',
                success: function(response) {
                    pageView.viewModel.loading(false);
                    viewModel.forms.remove(form);
                },
                error: function(response) {
                    pageView.viewModel.loading(false);
                    pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
                }
            });
        },
        selectedFormId: ko.observable(null)
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
