define([
  'knockout',
  'arches',
  'viewmodels/openable-workflow',
  'templates/views/components/plugins/default-workflow.htm',
  'views/components/workflows/default-card-util',
  'views/components/workflows/workflow-builder-initial-step',

  // Not the best way to implement this implemented but this will allow 
  // the use of custom components
  // 'views/components/workflows/{custom-component-name}.js',
], function (ko, arches, OpenableWorkflow, workflowTemplate) {
  return ko.components.register('workflow-builder-loader', {
    viewModel: function (params) {
      this.componentName = params.plugin.slug;

      this.stepConfig = params.stepConfig;

      OpenableWorkflow.apply(this, [params]);
      this.quitUrl = arches.urls.plugin('init-workflow');
    },
    template: workflowTemplate
  });
});
