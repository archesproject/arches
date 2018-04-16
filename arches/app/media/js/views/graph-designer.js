define([
    'jquery',
    'underscore',
    'knockout',
    'views/base-manager',
    'graph-designer-data',
    'arches',
    'viewmodels/graph-settings'
], function($, _, ko, BaseManagerView, data, arches, GraphSettingsViewModel) {

    var currentWidth, start;
    var viewModel = {
        dataFilter: ko.observable(''),
        placeholder: ko.observable(''),
        graphid: ko.observable(data.graphid),
        activeTab: ko.observable('graph'),
        viewState: ko.observable('design'),
        leftPanelFlex: ko.observable('0 0 270'),
        graphSettingsVisible: ko.observable(false),
        contentLoading: ko.observable(false)
    }

    viewModel.loadGraphSettings = function(){
        var el = $('.graph-designer-graph-content');
        var self = this;
        self.contentLoading(true);
        $.ajax({
            type: "GET",
            url: arches.urls.new_graph_settings(data.graphid),
            data: {'search': true, 'csrfmiddlewaretoken': '{{ csrf_token }}'}})
        .done(function(data){
            el.html(data['html']);
            self.graphSettingsViewModel = new GraphSettingsViewModel(data['data']);
            self.graphSettingsViewModel.contentLoading = self.contentLoading;
            ko.applyBindings(self.graphSettingsViewModel, el[0]);
            self.graphSettingsVisible(true);
            self.contentLoading(false);
        })
        .fail(function() {
          console.log( "error" );
      });
    };

    if (viewModel.activeTab() === 'graph') {
        viewModel.loadGraphSettings();
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
