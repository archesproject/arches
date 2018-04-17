define([
    'jquery',
    'underscore',
    'knockout',
    'views/base-manager',
    'graph-designer-data',
    'arches',
    'viewmodels/graph-settings',
    'bindings/resizable-sidepanel'
], function($, _, ko, BaseManagerView, data, arches, GraphSettingsViewModel) {

    var viewModel = {
        dataFilter: ko.observable(''),
        placeholder: ko.observable(''),
        graphid: ko.observable(data.graphid),
        activeTab: ko.observable('graph'),
        viewState: ko.observable('design'),
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

    return new BaseManagerView({
        viewModel: viewModel
    });
});
