define([
    'underscore',
    'knockout',
    'views/base-manager',
    'viewmodels/mobile-survey-manager',
    'viewmodels/alert',
    'models/mobile-survey',
    'mobile-survey-manager-data',
    'arches',
    'bindings/datepicker'
], function(_, ko, BaseManagerView, MobileSurveyManagerViewModel, AlertViewModel, MobileSurveyModel, data, arches) {
    
    var viewModel = new MobileSurveyManagerViewModel(data);

    viewModel.saveMobileSurvey = function() {
        var self = this;
        this.loading(true);
        var addMobileSurvey = !this.selectedMobileSurvey().get('id');
        this.selectedMobileSurvey().save(function() {
            if (addMobileSurvey) {
                self.mobilesurveys.push(self.selectedMobileSurvey());
            }
            self.loading(false);
        });
    }

    viewModel.discardEdits = function() {
        if (!this.selectedMobileSurvey().get('id')) {
            this.selectedMobileSurvey(null)
        } else {
            this.resourceList.resetCards(this.selectedMobileSurvey().get('source').cards)
            this.selectedMobileSurvey().reset();
        }
    }

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
                    tilecache: ''
                },
                identities: data.identities
            }));
        }
    }

    viewModel.deleteMobileSurvey = function(mobilesurvey){
        if (!mobilesurvey.active()) {
            var self = this;
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmSurveyDelete.title, arches.confirmSurveyDelete.text, function() {
                return;
            }, function(a){
                self.loading(true)
                if (mobilesurvey) {
                    mobilesurvey.delete(function(){
                        self.loading(false);
                        self.mobilesurveys.remove(mobilesurvey);
                    });
                    if (mobilesurvey === self.selectedMobileSurvey()) {
                        self.selectedMobileSurvey(undefined);
                    }
                };
            }));
        }
    }

    viewModel.deleteSelectedMobileSurvey = function(){
        if (this.selectedMobileSurvey()) {
            this.deleteMobileSurvey(this.selectedMobileSurvey())
            this.selectedMobileSurvey(undefined)
        };
    }

    if (viewModel.mobilesurveys().length === 0) {
        viewModel.newMobileSurvey()
    } else {
        viewModel.selectedMobileSurvey(viewModel.mobilesurveys()[0])
    }

    var pageView = new BaseManagerView({
        viewModel: viewModel
    });

    return pageView;
});
