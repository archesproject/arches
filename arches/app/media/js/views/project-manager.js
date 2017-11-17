define([
    'underscore',
    'knockout',
    'views/base-manager',
    'viewmodels/project-manager',
    'viewmodels/alert',
    'models/project',
    'project-manager-data',
    'arches',
    'bindings/datepicker'
], function(_, ko, BaseManagerView, ProjectManagerViewModel, AlertViewModel, ProjectModel, data, arches) {
    var viewModel = new ProjectManagerViewModel(data);

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
            this.selectedProject().reset();
        }
    }

    viewModel.newProject = function() {
        if (!this.selectedProject() || !this.selectedProject().dirty()) {
            this.selectedProject(new ProjectModel({
                source: {
                    name: '',
                    active: false,
                    description: '',
                    startdate: null,
                    enddate: null,
                    id: null,
                    cards: [],
                    users: [],
                    groups: []
                },
                identities: data.identities
            }));
        }
    }

    viewModel.deleteProject = function(project){
        if (!project.active()) {
            var self = this;
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmProjectDelete.title, arches.confirmProjectDelete.text, function() {
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

    viewModel.resourceList.items()[0].selected(true)

    var pageView = new BaseManagerView({
        viewModel: viewModel
    });

    return pageView;
});
