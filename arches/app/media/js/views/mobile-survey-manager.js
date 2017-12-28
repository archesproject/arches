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

    viewModel.saveProject = function() {
        var self = this;
        this.loading(true);
        var addProject = !this.selectedProject().get('id');
        this.selectedProject().save(function() {
            if (addProject) {
                self.projects.push(self.selectedProject());
            }
            self.loading(false);
        });
    }

    viewModel.discardEdits = function() {
        if (!this.selectedProject().get('id')) {
            this.selectedProject(null)
        } else {
            this.resourceList.resetCards(this.selectedProject().get('source').cards)
            this.selectedProject().reset();
        }
    }

    viewModel.newProject = function() {
        if (!this.selectedProject() || !this.selectedProject().dirty()) {
            this.selectedProject(new MobileSurveyModel({
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

    viewModel.deleteProject = function(project){
        if (!project.active()) {
            var self = this;
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmSurveyDelete.title, arches.confirmSurveyDelete.text, function() {
                return;
            }, function(a){
                self.loading(true)
                if (project) {
                    project.delete(function(){
                        self.loading(false);
                        self.projects.remove(project);
                    });
                    if (project === self.selectedProject()) {
                        self.selectedProject(undefined);
                    }
                };
            }));
        }
    }

    viewModel.deleteSelectedProject = function(){
        if (this.selectedProject()) {
            this.deleteProject(this.selectedProject())
            this.selectedProject(undefined)
        };
    }

    if (viewModel.projects().length === 0) {
        viewModel.newProject()
    } else {
        viewModel.selectedProject(viewModel.projects()[0])
    }

    var pageView = new BaseManagerView({
        viewModel: viewModel
    });

    return pageView;
});
