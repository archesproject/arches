define([
  'jquery',
  'knockout',
  'knockout-mapping',
  'arches',
  'templates/views/components/plugins/workflow-builder.htm',
  // 'plugins/knockout-select2'
], function ($, ko, koMapping, arches, pageTemplate) {
  const pageViewModel = function (params) {
    this.selectedResource = ko.observable();

    this.resources = ko.observable();
    this.workflows = ko.observable();

    this.openWorkflowBuilderWithGraph = (graphId) => {
      const url = `workflow-builder-editor?graph-id=${graphId}`;
      window.location.href = arches.urls.plugin(url);
    };

    this.openWorkflowBuilderWithWorkflow = (slug) => {
      const url = `workflow-builder-editor?workflow-id=${slug}`;
      window.location.href = arches.urls.plugin(url);
    };

    this.init = async () => {
      const workflows = await (
        await window.fetch(arches.urls.root + `workflow-builder/plugins`)
      ).json();
      this.workflows(workflows.workflows);
      const resources = await (
        await window.fetch(arches.urls.root + `workflow-builder/resources`)
      ).json();
      this.resources(resources.resources);
    };

    this.init();
  };

  return ko.components.register('workflow-builder', {
    viewModel: pageViewModel,
    template: pageTemplate
  });
});
