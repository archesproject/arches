define([
    'jquery',
    'underscore',
    'knockout',
    'uuid',
    'views/base-manager',
    'viewmodels/alert',
    'mobile-survey-manager-data',
    'arches',
    'bindings/datepicker'
], function($, _, ko, uuid, BaseManagerView, AlertViewModel, data, arches) {

    var MobileSurveysViewModel = function(params) {
        var self = this;
        this.dateFormat = 'YYYY-MM-DD';

        this.mobilesurveys = ko.observableArray(
            params.mobilesurveys.map(function(mobilesurvey) {
                mobilesurvey.createdbyName = ko.observable('Created by: ' + mobilesurvey.createdby_id);
                mobilesurvey.name = ko.observable(mobilesurvey.name);
                mobilesurvey.active = ko.observable(mobilesurvey.active);
                mobilesurvey.delete = function(successCallback, errorCallback) {
                    return $.ajax({
                        url: arches.urls.mobile_survey_manager,
                        data: JSON.stringify(this),
                        method: 'DELETE'
                    }).done(successCallback).fail(errorCallback);
                };
                return mobilesurvey;
            })
        );

        this.mobileSurveyFilter = ko.observable('');

        this.filteredMobileSurveys = ko.computed(function() {
            var filter = self.mobileSurveyFilter();
            var list = self.mobilesurveys();
            if (filter.length === 0) {
                return list;
            }
            return _.filter(list, function(mobilesurvey) {
                return mobilesurvey.name().toLowerCase().indexOf(filter.toLowerCase()) >= 0;
            });
        });

        this.loading = ko.observable(false);
    };

    var viewModel = new MobileSurveysViewModel(data);

    viewModel.navigateToEditor = function(survey) {
        window.location = arches.urls.mobile_survey_editor(survey.id);
    };

    viewModel.newMobileSurvey = function() {
        var surveyid = uuid.generate();
        window.location = arches.urls.mobile_survey_editor(surveyid);
    };

    viewModel.deleteMobileSurvey = function(mobilesurvey){
        if (!mobilesurvey.active()) {
            var self = this;
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmSurveyDelete.title, arches.confirmSurveyDelete.text, function() {
                return;
            }, function(){
                self.loading(true);
                if (mobilesurvey) {
                    mobilesurvey.delete(function(){
                        self.mobilesurveys.remove(mobilesurvey);
                        self.loading(false);
                    }, function(err) {
                        pageView.viewModel.alert(new AlertViewModel('ep-alert-red', err.title, err.message));
                    }
                    );
                }
            }));
        }
    };

    viewModel.deleteSelectedMobileSurvey = function(){
        if (this.selectedMobileSurvey()) {
            this.deleteMobileSurvey(this.selectedMobileSurvey());
        }
    };

    var pageView = new BaseManagerView({
        viewModel: viewModel
    });

    return pageView;
});
