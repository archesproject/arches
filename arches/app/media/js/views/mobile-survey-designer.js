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
], function(_, ko, BaseManagerView, MobileSurveyViewModel, AlertViewModel, MobileSurveyModel, Tree, data, arches) {

    var viewModel = new MobileSurveyViewModel(data);
    viewModel.arches = arches;
    viewModel.saveMobileSurvey = function() {
        this.loading(true);
        var self = this;
        this.mobilesurvey.save(function(data) {
            if (data.responseJSON.success) {
                console.log('saved!');
            } else {
                pageView.viewModel.alert(new AlertViewModel('ep-alert-red', data.responseJSON.title, data.responseJSON.message));
            }
            self.loading(false);
        });
    };

    viewModel.tree = new Tree({
        mobilesurvey: viewModel.mobilesurvey,
        items: [{
            name: viewModel.mobilesurvey.name,
            selected: true,
            istopnode: true,
            expanded: ko.observable(true),
            childNodes: ko.observableArray([{
                name: 'Map Extent',
                selected: false,
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'Offline Maps',
                selected: false,
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'Models',
                selected: false,
                childNodes: ko.observableArray([{
                    name: 'Model 1',
                    selected: false,
                    childNodes: ko.observableArray([]),
                    expanded: ko.observable(false)
                },]),
                expanded: ko.observable(false)
            },
            {
                name: 'Data',
                selected: false,
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'People',
                selected: false,
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            }
            ])
        }]
    });
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
