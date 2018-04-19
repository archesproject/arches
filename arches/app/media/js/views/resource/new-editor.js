define([
    'underscore',
    'knockout',
    'views/base-manager',
    'resource-editor-data',
    'bindings/resizable-sidepanel'
], function(_, ko, BaseManagerView, data) {
    console.log(data);
    var viewModel = {
        graphid: ko.observable(data.graphid)
    }

    return new BaseManagerView({
        viewModel: viewModel
    });
});
