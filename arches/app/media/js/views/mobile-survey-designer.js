define([
    'underscore',
    'knockout',
    'views/base-manager',
    'viewmodels/mobile-survey',
    'viewmodels/alert',
    'models/mobile-survey',
    'mobile-survey-manager-data',
    'arches',
    'bindings/datepicker'
], function(_, ko, BaseManagerView, MobileSurveyViewModel, AlertViewModel, MobileSurveyModel, data, arches) {

    var viewModel = new MobileSurveyViewModel(data);
    viewModel.arches = arches;
    viewModel.saveMobileSurvey = function() {
        this.loading(true);
        var self = this;
        this.mobilesurvey.save(function(data) {
            if (data.responseJSON.success) {
                console.log('saved!')
            } else {
                pageView.viewModel.alert(new AlertViewModel('ep-alert-red', data.responseJSON.title, data.responseJSON.message));
            }
            self.loading(false);
        });
    };

    viewModel.discardEdits = function() {
        this.resourceList.resetCards(this.mobilesurvey.get('source').cards);
        this.mobilesurvey.reset();
    };

    viewModel.deleteMobileSurvey = function(mobilesurvey){
        if (!mobilesurvey.active()) {
            var self = this;
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmSurveyDelete.title, arches.confirmSurveyDelete.text, function() {
                return;
            }, function(){
                self.loading(true);
                if (mobilesurvey) {
                    mobilesurvey.delete(function(data){
                        if (data.responseJSON.success){
                            console.log('navigate back to manager page');
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
