define([
    'underscore',
    'knockout',
    'views/base-manager',
    'graph-designer-data'
], function(_, ko, BaseManagerView, data) {

    var currentWidth, start;
    var viewModel = {
        dataFilter: ko.observable(''),
        placeholder: ko.observable(''),
        graphid: ko.observable(data.graphid),
        activeTab: ko.observable('graph'),
        viewState: ko.observable('design'),
        leftPanelFlex: ko.observable('0 0 270'),
    }

    if (viewModel.activeTab() === 'graph') {
        // here we might load data/views asyncronously 
    }else{

    }

    if (viewModel.viewState() === 'design') {
        // here we might load data/views asyncronously 
    }else{

    }

    document.getElementById('draggable').ondragstart = function(e) {
        start = e.pageX;
        currentWidth = $('#left-panel').width();
    };
    document.addEventListener('dragover', function(e){
        e = e || window.event;
        var dragX = e.pageX, dragY = e.pageY;
        var width = start - dragX;

        viewModel.leftPanelFlex('0 0 ' + (currentWidth - width + 15) + 'px');
    }, false);

    return new BaseManagerView({
        viewModel: viewModel
    });
});
