require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'views/resource/editor/form-list',
    'views/resource/editor/form',
    'models/card',
    'viewmodels/provisional-tile',
    'viewmodels/alert',
    'resource-editor-data',
    'bindings/sortable',
    'bindings/let'
], function($, _, ko, arches, BaseManagerView, FormList, FormView, CardModel, ProvisionalTileViewModel, AlertViewModel, data) {
    var self = this;
    var loading = ko.observable(false);
    var cardLoading = ko.observable(false);
    var selectedForm = ko.observable();
    var provisionalLoading = ko.observable(false);
    var formList = new FormList({
        forms: ko.observableArray(data.forms)
    });
    formList.selectItem(formList.items()[0]);

    var selectedProvisionalTile = ko.observable()

    var provisionalTileViewModel = new ProvisionalTileViewModel(
        {
            selectedProvisionalTile: selectedProvisionalTile,
            cardModel: CardModel,
            selectedForm: selectedForm,
            loading: provisionalLoading
        }
    );

    var formView = new FormView({
        formid: formList.items()[0].formid,
        resourceid: data.resourceid,
        tiles: data.tiles,
        blanks: data.blanks,
        selectedProvisionalTile: selectedProvisionalTile,
        provisionalTileViewModel: provisionalTileViewModel
    });

    var loadForm = function(form) {
        loading(true);
        formView.loadForm(form.formid, function(){
            loading(false);
        });
    };

    formList.on('item-clicked', function(form){
        if (pageView.viewModel.dirty()) {
            pageView.viewModel.alert(new AlertViewModel('ep-alert-blue', arches.confirmNav.title, arches.confirmNav.text, function(){
                pageView.viewModel.showConfirmNav(false);
            }, function() {
                loadForm(form);
            }));
        } else {
            loadForm(form);
        }
    });

    formView.on('before-update', function(){
        cardLoading(true);
    });
    formView.on('after-update', function(response){
        cardLoading(false);
        var errorMessageTitle = arches.requestFailed.title
        var errorMessageText = arches.requestFailed.text
        pageView.viewModel.alert(null);
        if(response.status != 200){
            if (response.responseJSON) {
              errorMessageTitle = response.responseJSON.message[0]
              errorMessageText = response.responseJSON.message[1]
            }
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', errorMessageTitle, errorMessageText));
        }
    });

    /**
    * a PageView representing the resource listing and recent edits page
    */
    var pageView = new BaseManagerView({
        viewModel:{
            loading: loading,
            cardLoading: cardLoading,
            resourceEditorContext: true,
            editingInstanceId: data.resourceid,
            relationship_types: data.relationship_types,
            provisionalTileViewModel: provisionalTileViewModel,
            graph: data.graph,
            formList: formList,
            formView: formView,
            dirty: ko.computed(function() {
                var dirty = false;
                _.each(formView.formTiles(), function (tile) {
                    if (tile.dirty()) {
                        dirty = true;
                    }
                });
                return dirty;
            })
        }
    });

});
