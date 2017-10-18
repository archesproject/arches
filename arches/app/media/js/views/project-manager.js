define([
    'knockout',
    'views/base-manager',
    'models/project',
    'project-manager-data',
    'arches'
], function(ko, BaseManagerView, ProjectModel, data, arches) {
    var projects = ko.observableArray(
        data.projects.map(function (project) {
            return new ProjectModel({
                source: project
            });
        })
    );
    var loading = ko.observable(false);
    var selectedProject = ko.observable(null);
    var pageView = new BaseManagerView({
        viewModel: {
            loading: loading,
            projects: projects,
            selectedProject: selectedProject,
            saveProject: function () {
                loading(true);
                var addProject = !selectedProject().get('id');
                selectedProject().save(function () {
                    if (addProject) {
                        projects.push(selectedProject());
                    }
                    loading(false);
                });
            },
            discardEdits: function () {
                if (!selectedProject().get('id')) {
                    selectedProject(null)
                } else {
                    selectedProject().reset();
                }
            },
            newProject: function () {
                if (!selectedProject() || !selectedProject().dirty()) {
                    selectedProject(new ProjectModel({
                        source: {
                            name: '',
                            active: false,
                            id: null
                        }
                    }));
                }
            }
        }
    });

    return pageView;
});
