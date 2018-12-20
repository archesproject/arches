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
    viewModel.activePage = ko.observable('root');
    viewModel.tree = new Tree({
        activepage: viewModel.activePage,
        mobilesurvey: viewModel.mobilesurvey,
        items: [{
            name: viewModel.mobilesurvey.name,
            id: 'root',
            selected: ko.observable(true),
            istopnode: true,
            iconclass: 'fa fa-globe',
            pageactive: ko.observable(true),
            expanded: ko.observable(true),
            childNodes: ko.observableArray([{
                name: 'Map Extent',
                id: 'mapextent',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-map-marker',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'Map Sources',
                id: 'mapsources',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-th',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'Models',
                id: 'models',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-bookmark',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([{
                    name: 'Model 1',
                    id: 'model1',
                    pageid: 'models',
                    selected: ko.observable(false),
                    istopnode: false,
                    iconclass: 'fa fa-globe',
                    childNodes: ko.observableArray([]),
                    expanded: ko.observable(false)
                },]),
                expanded: ko.observable(false)
            },
            {
                name: 'Data',
                id: 'data',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-bar-chart-o',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'People',
                id: 'people',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-group',
                pageactive: ko.observable(false),
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
