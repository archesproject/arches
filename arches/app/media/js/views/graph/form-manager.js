require([
    'underscore',
    'knockout',
    'models/graph',
    'views/graph/graph-page-view',
    'arches',
    'graph-forms-data',
], function(_, ko, GraphModel, PageView, arches, data) {

    /**
    * a PageView representing the graph forms page
    */
    var self = this;

    _.each(data.forms, function(form) {
        form.cards = _.map(form.cards, function (cardId) {
            return _.find(data.cards, function (card) {
                return card.cardid === cardId;
            });
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
        forms: data.forms,
        formOptions: options.concat(data.forms),
        openForm: function (formId) {
            pageView.viewModel.navigate(arches.urls.form_configuration + formId);
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
