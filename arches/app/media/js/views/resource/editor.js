require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'views/resource/editor/form-list',
    'views/resource/editor/form',
    'models/card',
    'viewmodels/alert',
    'resource-editor-data',
    'bindings/sortable',
    'bindings/let'
], function($, _, ko, arches, BaseManagerView, FormList, FormView, CardModel, AlertViewModel, data) {
    var self = this;
    var formList = new FormList({
        forms: ko.observableArray(data.forms)
    })
    formList.selectItem(formList.items()[0]);
    
    var formView = new FormView({
        formid: formList.items()[0].formid,
        resourceid: data.resourceid,
        tiles: data.tiles,
        blanks: data.blanks
    })

    formList.on('item-clicked', function(form){
        pageView.viewModel.loading(true);
        formView.loadForm(form.formid, function(){
            pageView.viewModel.loading(false);
        });
    });

    formView.on('before-update', function(){
        pageView.viewModel.loading(true);
    });
    formView.on('after-update', function(response){
        pageView.viewModel.loading(false);
        if(response.status != 200){
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));   
        }
    });


    /**
    * a PageView representing the resource listing and recent edits page
    */
    var pageView = new BaseManagerView({
        viewModel:{
            formList: formList,
            formView: formView,
            deleteResource: function(){
                pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmResourceDelete.title, arches.confirmResourceDelete.text, function() {
                    return;
                }, function(){
                    pageView.viewModel.loading(true);
                    $.ajax({
                        type: "DELETE",
                        url: arches.urls.resource_editor + data.resourceid,
                        success: function(response) {
                        
                        },
                        error: function(response) {

                        },
                        complete: function (request, status) {
                            pageView.viewModel.loading(false);
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
