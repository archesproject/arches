define([
    'underscore',
    'knockout',
    'views/project-manager/identity-list',
    'models/project'
], function(_, ko, IdentityList, ProjectModel) {
    /**
    * A base viewmodel for project management
    *
    * @constructor
    * @name ProjectManagerViewModel
    *
    * @param  {string} params - a configuration object
    */
    var ProjectManagerViewModel = function(params) {
        var self = this;
        this.dateFormat = 'YYYY-MM-DD';

        this.identityList = new IdentityList({
            items: ko.observableArray(params.identities)
        });
        this.projects = ko.observableArray(
            params.projects.map(function (project) {
                return new ProjectModel({
                    source: project,
                    identities: params.identities
                });
            })
        );
        this.projectFilter = ko.observable('');
        this.filteredProjects = ko.computed(function () {
            var filter = self.projectFilter();
            var list = self.projects();
            if (filter.length === 0) {
                return list;
            }
            return _.filter(list, function(project) {
                return project.name().toLowerCase().indexOf(filter.toLowerCase()) >= 0;
            });
        });

        this.loading = ko.observable(false);
        this.selectedProject = ko.observable(null);

        this.selectedProject.subscribe(function(val){
            if (val) {
                self.identityList.clearSelection();
                self.identityList.items()[0].selected(true);
                val.update();
            }
        });

    };
    return ProjectManagerViewModel;
});
