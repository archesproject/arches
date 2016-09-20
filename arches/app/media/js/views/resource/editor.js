require([
    'jquery',
    'underscore',
    'knockout',
    'views/page-view',
    'views/resource/editor/form-list',
    'resource-editor-data',
], function($, _, ko, PageView, FormList, data) {

    var formList = new FormList({
        forms: ko.observableArray(data.forms)
    })

    /**
    * a PageView representing the resource listing and recent edits page
    */
    var pageView = new PageView({
        viewModel:{
            formList: formList
        }
    });

});
