define([
    'underscore',
    'knockout',
    'views/base-manager',
    'graph-designer-data',
    'bindings/resizable-sidepanel'
], function(_, ko, BaseManagerView, data) {
    var viewModel = {
        dataFilter: ko.observable(''),
        placeholder: ko.observable(''),
        graphid: ko.observable(data.graphid),
        activeTab: ko.observable('graph'),
        viewState: ko.observable('design')
    }

    if (viewModel.activeTab() === 'graph') {
        // here we might load data/views asyncronously
    }else{

    }

    if (viewModel.viewState() === 'design') {
        // here we might load data/views asyncronously
    }else{

    }

    return new BaseManagerView({
        viewModel: viewModel
    });
});
