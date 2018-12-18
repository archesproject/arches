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
    viewModel.selectedMobileSurvey(new MobileSurveyModel({source: data.mobilesurveys[0], identities: data.identities}));
    viewModel.arches = arches;
    viewModel.saveMobileSurvey = function() {
        this.loading(true);
        var self = this;
        var addMobileSurvey = !this.selectedMobileSurvey().get('id');
        this.selectedMobileSurvey().save(function(data) {
            if (data.responseJSON.success) {
                if (addMobileSurvey) {
                    self.mobilesurveys.push(self.selectedMobileSurvey());
                }
            } else {
                pageView.viewModel.alert(new AlertViewModel('ep-alert-red', data.responseJSON.title, data.responseJSON.message));
            }
            self.loading(false);
        });
    };

    viewModel.discardEdits = function() {
        if (!this.selectedMobileSurvey().get('id')) {
            this.selectedMobileSurvey(null);
        } else {
            this.resourceList.resetCards(this.selectedMobileSurvey().get('source').cards);
            this.selectedMobileSurvey().reset();
        }
    };

    viewModel.newMobileSurvey = function() {
        if (!this.selectedMobileSurvey() || !this.selectedMobileSurvey().dirty()) {
            this.selectedMobileSurvey(new MobileSurveyModel({
                source: {
                    name: '',
                    active: false,
                    description: '',
                    startdate: null,
                    enddate: null,
                    id: null,
                    cards: [],
                    users: [],
                    groups: [],
                    bounds: null,
                    datadownloadconfig: {download:false, count:1000, resources:[], custom: null},
                    tilecache: '',
                    onlinebasemap: ''
                },
                identities: data.identities
            }));
        }
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
                            self.mobilesurveys.remove(mobilesurvey);
                            if (mobilesurvey === self.selectedMobileSurvey()) {
                                self.selectedMobileSurvey(undefined);
                            }
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
        if (this.selectedMobileSurvey()) {
            this.deleteMobileSurvey(this.selectedMobileSurvey());
        }
    };

    if (viewModel.mobilesurveys().length === 0) {
        viewModel.newMobileSurvey();
    } else {
        viewModel.selectedMobileSurvey(viewModel.mobilesurveys()[0]);
    }

    var pageView = new BaseManagerView({
        viewModel: viewModel
    });

    return pageView;
});
