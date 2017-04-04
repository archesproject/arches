require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/search-base-manager',
    'views/resource/editor/form-list',
    'views/resource/editor/form',
    'models/card',
    'viewmodels/alert',
    'resource-editor-data',
    'bindings/sortable',
    'bindings/let'
], function($, _, ko, arches, SearchBaseManagerView, FormList, FormView, CardModel, AlertViewModel, data) {
    var self = this;
    var loading = ko.observable(false);
    var formList = new FormList({
        forms: ko.observableArray(data.forms)
    });
    formList.selectItem(formList.items()[0]);

    var formView = new FormView({
        formid: formList.items()[0].formid,
        resourceid: data.resourceid,
        tiles: data.tiles,
        blanks: data.blanks
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
        loading(true);
    });
    formView.on('after-update', function(response){
        loading(false);
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
    var pageView = new SearchBaseManagerView({
        viewModel:{
            loading: loading,
            resourceEditorContext: true,
            editingInstanceId: data.resourceid,
            relationship_types: data.relationship_types,
            graph: data.graph,
            formList: formList,
            formView: formView,
            openRelatedResources: ko.observable(false),
            dirty: ko.computed(function() {
                var dirty = false;
                _.each(formView.formTiles(), function (tile) {
                    if (tile.dirty()) {
                        dirty = true;
                    }
                });
                return dirty;
            }),
            deleteResource: function(){
                pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmResourceDelete.title, arches.confirmResourceDelete.text, function() {
                    return;
                }, function(){
                    loading(true);
                    $.ajax({
                        type: "DELETE",
                        url: arches.urls.resource_editor + data.resourceid,
                        success: function(response) {

                        },
                        error: function(response) {

                        },
                        complete: function (request, status) {
                            loading(false);
                            if (status === 'success') {
                                pageView.viewModel.navigate(arches.urls.resource);
                            }
                        },
                    });
                }));
            }
        }
    });

});
