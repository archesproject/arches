require([
    'knockout',
    'arches',
    'models/graph',
    'models/form',
    'views/graph/form-settings',
    'views/graph/graph-page-view',
    'views/list',
    'form-configuration-data'
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

    var viewModel = {
        formOptions: options.concat(data.forms),
        formSettings: new FormSettingsView({formModel:formModel}),
        graphModel: new GraphModel({
            data: data.graph
        }),

        cardList: new ListView({
            items: ko.observableArray(data.cards)
        }),
        selectedFormId: ko.observable(null),
        openForm: function (formId) {
            pageView.viewModel.navigate(arches.urls.form_configuration + formId);
        },
        addCard: function() {

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
