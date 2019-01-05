define([
    'underscore',
    'knockout',
    'views/base-manager',
    'viewmodels/mobile-survey',
    'viewmodels/alert',
    'models/mobile-survey',
    'views/mobile-survey-manager/mobile-survey-tree',
    'mobile-survey-manager-data',
    'arches',
    'bindings/datepicker',
    'bindings/resizable-sidepanel',
    'bindings/select2-query'
], function(_, ko, BaseManagerView, MobileSurveyViewModel, AlertViewModel, MobileSurveyModel, Tree, data, arches) {

    var viewModel = new MobileSurveyViewModel(data);
    viewModel.arches = arches;
    viewModel.saveMobileSurvey = function() {
        this.loading(true);
        var self = this;
        this.mobilesurvey.save(function(data) {
            if (!data.responseJSON.success) {
                pageView.viewModel.alert(new AlertViewModel('ep-alert-red', data.responseJSON.title, data.responseJSON.message));
            }
            self.loading(false);
        });
    };

    viewModel.activePage = ko.observable('root');
    viewModel.selectedNode = ko.observable(viewModel.treenodes[0]);
    viewModel.tree = new Tree({
        activepage: viewModel.activePage,
        mobilesurvey: viewModel.mobilesurvey,
        items: viewModel.treenodes,
        selectednode: viewModel.selectedNode,
        status: viewModel.surveyReady
    });

    viewModel.discardEdits = function() {
        this.mobilesurvey.reset();
        this.resetCards(this.mobilesurvey.cards);
        this.resetIdentities(this.mobilesurvey);
        this.treenodes[0].selected(true);
        this.activePage('root');
        _.each(this.treenodes[0].childNodes(), function(node){
            node.selected(false);
            node.expanded(false);
        });
    };

    viewModel.deleteMobileSurvey = function(){
        if (!this.mobilesurvey.active()) {
            var self = this;
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmSurveyDelete.title, arches.confirmSurveyDelete.text, function() {
                return;
            }, function(){
                self.loading(true);
                if (self.mobilesurvey) {
                    self.mobilesurvey.delete(function(data){
                        if (data.responseJSON.success){
                            self.navigateToManager();
                        } else {
                            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', data.responseJSON.title, data.responseJSON.message));
                        }
                        self.loading(false);
                    });
                }
            }));
        }
    };

    viewModel.deleteSelectedMobileSurvey = function(){
        if (this.mobilesurvey) {
            this.deleteMobileSurvey(this.mobilesurvey);
        }
    };

    var pageView = new BaseManagerView({
        viewModel: viewModel
    });

    return pageView;
});
