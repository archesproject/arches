define([
    'underscore',
    'knockout',
    'views/base-manager',
    'viewmodels/project-manager',
    'models/project',
    'project-manager-data',
    'arches'
], function(_, ko, BaseManagerView, ProjectManagerViewModel, ProjectModel, data, arches) {
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

    var pageView = new BaseManagerView({
        viewModel: viewModel
    });

    return pageView;
});
