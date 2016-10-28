require([
    'jquery',
    'underscore',
    'knockout',
    'views/base-manager',
    'views/resource/editor/form-list',
    'views/resource/editor/form',
    'models/card',
    'resource-editor-data',
    'bindings/sortable',
    'bindings/let'
], function($, _, ko, BaseManagerView, FormList, FormView, CardModel, data) {
    var self = this;
    var formView = new FormView({
        formid: data.forms[0].formid,
        resourceid: data.resourceid,
        tiles: data.tiles,
        blanks: data.blanks
    })
    var formList = new FormList({
        forms: ko.observableArray(data.forms)
    })

    formList.on('item-selected', function(form){
        pageView.viewModel.loading(true);
        formView.loadForm(form.formid, function(){
            pageView.viewModel.loading(false);
        });
    });


    /**
    * a PageView representing the resource listing and recent edits page
    */
    var pageView = new BaseManagerView({
        viewModel:{
            formList: formList,
            formView: formView,
        }
    });

});
