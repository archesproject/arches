define([
    'knockout',
    'jquery',
    'arches',
    'viewmodels/workflow',
    'viewmodels/workflow-step',
    'views/components/workflows/create-project-workflow/project-name-step',
    'views/components/workflows/create-project-workflow/add-things-step',
    'views/components/workflows/create-project-workflow/create-project-final-step'
], function(ko, $, arches, Workflow) {
    return ko.components.register('create-project-workflow', {
        viewModel: function(params) {
            this.componentName = 'create-project-workflow';

            this.stepConfig = [
                {
                    title: 'Project Name',
                    name: 'set-project-name',  /* unique to workflow */
                    required: true,
                    informationboxdata: {
                        heading: 'Project Name',
                        text: 'Identify the project by giving it a name',
                    },
                    layoutSections: [
                        {
                            componentConfigs: [
                                {
                                    componentName: 'project-name-step',
                                    uniqueInstanceName: 'project-name', /* unique to step */
                                    parameters: {
                                    },
                                },
                            ], 
                        },
                    ]
                },
                {
                    title: 'Project Statement',
                    name: 'set-project-statement',  /* unique to workflow */
                    required: false,
                    informationboxdata: {
                        heading: 'Project Statement',
                        text: 'Indicate the objectives or motivation of the project',
                    },
                    layoutSections: [
                        {
                            componentConfigs: [
                                {
                                    componentName: 'default-card',
                                    uniqueInstanceName: 'project-statement', /* unique to step */
                                    tilesManaged: 'one',
                                    parameters: {
                                        graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                                        nodegroupid: '0b92a414-ca85-11e9-b725-a4d18cec433a',
                                        resourceid: "['set-project-name']['project-name']['projectResourceId']",
                                    },
                                },
                            ], 
                        },
                    ],
                },
                {
                    title: 'Project Start',
                    name: 'set-project-timespan',  /* unique to workflow */
                    required: false,
                    informationboxdata: {
                        heading: 'Project Start',
                        text: 'Indicate the date the project started if known',
                    },
                    layoutSections: [
                        {
                            componentConfigs: [
                                {
                                    componentName: 'default-card',
                                    uniqueInstanceName: 'project-timespan', /* unique to step */
                                    tilesManaged: 'one',
                                    parameters: {
                                        graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                                        nodegroupid: '0b925e3a-ca85-11e9-a308-a4d18cec433a',
                                        resourceid: "['set-project-name']['project-name']['projectResourceId']",
                                        hiddenNodes: ['0b92f57d-ca85-11e9-a353-a4d18cec433a', '0b931623-ca85-11e9-b235-a4d18cec433a', '0b930905-ca85-11e9-8aca-a4d18cec433a'],
                                    },
                                },
                            ], 
                        },
                    ],
                },
                {
                    title: 'Project Team',
                    name: 'set-project-team',  /* unique to workflow */
                    required: false,
                    informationboxdata: {
                        heading: 'Project Team',
                        text: 'Add the names of people involved in the project',
                    },                    
                    layoutSections: [
                        {
                            componentConfigs: [
                                {
                                    componentName: 'default-card',
                                    uniqueInstanceName: 'project-team', /* unique to step */
                                    tilesManaged: 'one',
                                    parameters: {
                                        graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                                        nodegroupid: 'dbaa2022-9ae7-11ea-ab62-dca90488358a',
                                        resourceid: "['set-project-name']['project-name']['projectResourceId']",
                                    },
                                },
                            ], 
                        },
                    ],
                },
                {
                    title: 'Add Objects to Your Project',
                    name: 'object-search-step',  /* unique to workflow */
                    required: true,
                    workflowstepclass: 'create-project-add-things-step',
                    informationboxdata: {
                        heading: 'Add Objects',
                        text: 'Add Objects to Your Project',
                    },
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
                                        resourceid: "['set-project-name']['project-name']['projectResourceId']",
                                        projectStepData: "['set-project-name']['project-name']"
                                    },
                                },
                            ],
                        },
                    ],
                },
                {
                    title: 'Summary',
                    name: 'add-project-complete',  /* unique to workflow */
                    description: 'Summary',
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'create-project-final-step',
                                    uniqueInstanceName: 'create-project-final',
                                    tilesManaged: 'none',
                                    parameters: {
                                        resourceid: "['set-project-name']['project-name']['projectResourceId']",
                                        collectionResourceId: "['object-search-step']['add-phys-things'][0]['collectionResourceId']",
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
        template: { require: 'text!templates/views/components/plugins/create-project-workflow.htm' }
    });
});
