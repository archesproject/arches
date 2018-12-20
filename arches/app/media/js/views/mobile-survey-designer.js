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

    var nodes = [{
        name: viewModel.mobilesurvey.name,
        namelong: 'Summary',
        description: 'Survey summary and status',
        id: 'root',
        selected: ko.observable(true),
        istopnode: true,
        iconclass: 'fa fa-globe',
        pageactive: ko.observable(true),
        expanded: ko.observable(true),
        childNodes: ko.observableArray([{
            name: 'Settings',
            namelong: 'Survey Settings',
            description: 'Define data collection parameters for your survey',
            id: 'settings',
            selected: ko.observable(false),
            istopnode: false,
            iconclass: 'fa fa-wrench',
            pageactive: ko.observable(false),
            childNodes: ko.observableArray([]),
            expanded: ko.observable(false)
        },
        {
            name: 'Map Extent',
            namelong: 'Map Extent',
            description: 'Draw a polygon to define the area over which you want to collect data in this survery',
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
            namelong: 'Basemap Source',
            description: 'Provide a basemap source url. Use an offline source for users without access to cell/wi-fi service',
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
            namelong: 'Models',
            description: 'Summary of models in this survey',
            id: 'models',
            selected: ko.observable(false),
            istopnode: false,
            iconclass: 'fa fa-bookmark',
            pageactive: ko.observable(false),
            childNodes: ko.observableArray([{
                name: 'Model 1',
                namelong: 'Model Details',
                description: 'Summary of how this model participates in the survey',
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
            namelong: 'Data download',
            description: 'Define the data you will allow users to download',
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
            namelong: 'People',
            description: 'Summary of people invited to participate in this survey',
            id: 'people',
            selected: ko.observable(false),
            istopnode: false,
            iconclass: 'fa fa-group',
            pageactive: ko.observable(false),
            childNodes: ko.observableArray([]),
            expanded: ko.observable(false)
        }
        ])
    }];

    viewModel.activePage = ko.observable('root');
    viewModel.selectedNode = ko.observable(nodes[0]);

    viewModel.tree = new Tree({
        activepage: viewModel.activePage,
        mobilesurvey: viewModel.mobilesurvey,
        items: nodes,
        selectednode: viewModel.selectedNode
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
