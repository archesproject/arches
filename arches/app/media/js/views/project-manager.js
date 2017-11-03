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
                    id: null
                },
                identities: data.identities
            }));
        }
    }

    viewModel.deleteProject = function(){
        var self = this;
        pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmProjectDelete.title, arches.confirmProjectDelete.text, function() {
            return;
        }, function(a){
            self.loading(true)
            if (self.selectedProject()) {
                self.selectedProject().delete(function(){
                    self.loading(false);
                    self.projects.remove(self.selectedProject());
                    self.selectedProject(undefined)
                });
            };
        }));
    }

    var pageView = new BaseManagerView({
        viewModel: viewModel
    });

    return pageView;
});
