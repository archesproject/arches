define([
    'jquery',
    'underscore',
    'knockout',
    'uuid',
    'views/base-manager',
    'viewmodels/alert',
    'viewmodels/alert-json',
    'mobile-survey-manager-data',
    'arches',
    'moment',
    'bindings/datepicker',
], function($, _, ko, uuid, BaseManagerView, AlertViewModel, JsonErrorAlertViewModel, data, arches, moment) {

    var MobileSurveysViewModel = function(params) {
        var self = this;
        this.dateFormat = 'YYYY-MM-DD';
        this.mobilesurveys = ko.observableArray(
            params.mobilesurveys.map(function(mobilesurvey) {
                mobilesurvey.createdbyName = mobilesurvey.created_by.first + ' ' + mobilesurvey.created_by.last;
                mobilesurvey.name = ko.observable(mobilesurvey.name);
                mobilesurvey.active = ko.observable(mobilesurvey.active);
                mobilesurvey.ends = moment(mobilesurvey.enddate).format('D MMMM YYYY');
                mobilesurvey.starts = moment(mobilesurvey.startdate).format('D MMMM YYYY');
                mobilesurvey.delete = function(successCallback, errorCallback) {
                    return $.ajax({
                        url: arches.urls.collector_manager,
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
        window.location = arches.urls.collector_designer(survey.id);
    };

    viewModel.newMobileSurvey = function() {
        var surveyid = uuid.generate();
        window.location = arches.urls.collector_designer(surveyid);
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
