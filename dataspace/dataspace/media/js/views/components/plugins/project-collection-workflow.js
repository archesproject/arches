define([
    'knockout',
    'jquery',
    'arches',
    'viewmodels/workflow',
    'viewmodels/workflow-step',
    'views/components/workflows/select-phys-thing-step',
    'views/components/workflows/create-project-workflow/add-things-step',
    'views/components/workflows/project-collection-workflow/project-collection-final-step'
], function(ko, $, arches, Workflow) {
    return ko.components.register('project-collection-workflow', {
        viewModel: function(params) {
            this.componentName = 'project-collection-workflow';

            this.stepConfig = [
                {
                    title: 'Select Project',
                    name: 'select-project',  /* unique to workflow */
                    required: true,
                    informationboxdata: {
                        heading: 'Select Project',
                        text: 'Select a project to update',
                    },
                    layoutSections: [
                        {
                            sectionTitle: 'Select Project',
                            componentConfigs: [
                                {
                                    componentName: 'resource-instance-select-widget',
                                    uniqueInstanceName: 'select-project', /* unique to step */
                                    parameters: {
                                        graphids: [
                                            '0b9235d9-ca85-11e9-9fa2-a4d18cec433a'/* Project */
                                        ],
                                    },
                                },
                            ], 
                        },
                    ],
                },
                {
                    title: 'Add Objects to Your Project',
                    name: 'object-search-step',  /* unique to workflow */
                    required: false,
                    workflowstepclass: 'create-project-add-things-step',
                    informationboxdata: {
                        heading: 'Update Objects',
                        text: 'Update Objects in Your Project',
                    },
                    lockableExternalSteps: ['select-project'],
                    layoutSections: [
                        {
                            componentConfigs: [
                                {
                                    componentName: 'add-things-step',
                                    uniqueInstanceName: 'add-phys-things',
                                    tilesManaged: 'one',
                                    parameters: {
                                        graphid: '1b210ef3-b25c-11e9-a037-a4d18cec433a', //Collection graph
                                        nodegroupid: '466f81d4-c451-11e9-b7c9-a4d18cec433a', //Curation in Collection
                                        nodeid: '466fa421-c451-11e9-9a6d-a4d18cec433a', //Curation_used in Collection (physical thing)
                                        resourceid: "['select-project']['select-project']",
                                        action: "update",
                                    },
                                },
                            ],
                        },
                    ],
                },
                {
                    title: 'Summary',
                    name: 'project-collection-complete',  /* unique to workflow */
                    description: 'Summary',
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'project-collection-final-step',
                                    uniqueInstanceName: 'project-collection-final',
                                    tilesManaged: 'none',
                                    parameters: {
                                        projectResourceId: "['select-project']['select-project']",
                                        resourceid: "['object-search-step']['add-phys-things'][0]['collectionResourceId']",
                                    },
                                },
                            ], 
                        },
                    ],
                }
            ];

            Workflow.apply(this, [params]);
            this.quitUrl = arches.urls.plugin('init-workflow');
        },
        template: { require: 'text!templates/views/components/plugins/project-collection-workflow.htm' }
    });
});
