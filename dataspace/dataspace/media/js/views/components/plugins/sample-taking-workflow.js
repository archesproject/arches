define([
    'knockout',
    'jquery',
    'arches',
    'viewmodels/workflow',
    'viewmodels/workflow-step',
    'views/components/workflows/select-phys-thing-step',
    'views/components/workflows/sample-taking-workflow/sampling-info-step',
    'views/components/workflows/sample-taking-workflow/sample-taking-sample-location-step',
    'views/components/workflows/sample-taking-workflow/sample-taking-image-step',
    'views/components/workflows/sample-taking-workflow/sample-taking-final-step'
], function(ko, $, arches, Workflow) {
    return ko.components.register('sample-taking-workflow', {
        viewModel: function(params) {
            this.componentName = 'sample-taking-workflow';

            this.stepConfig = [
                {
                    title: 'Project Info',
                    name: 'select-project',  /* unique to workflow */
                    required: true,
                    informationboxdata: {
                        heading: 'Projects and related object',
                        text: 'Select the project and object that you are sampling',
                    },
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'select-phys-thing-step',
                                    uniqueInstanceName: 'select-phys-thing', /* unique to step */
                                    parameters: {
                                        graphids: [
                                            '9519cb4f-b25b-11e9-8c7b-a4d18cec433a', /* Project */
                                            '0b9235d9-ca85-11e9-9fa2-a4d18cec433a'/* Physical Thing */
                                        ],  
                                    },
                                },
                            ], 
                        },
                    ],
                },
                {
                    title: 'Sampling Activity Info',
                    name: 'sample-info',  /* unique to workflow */
                    description: 'The date that the sample was taken',
                    informationboxdata: {
                        heading: 'Sampling Information',
                        text: 'Enter the people, date, method, and notes describing the sampling activities on the object',
                    },
                    required: true,
                    lockableExternalSteps: ['select-project'],
                    layoutSections: [
                        {
                            sectionTitle: null,
                            componentConfigs: [
                                { 
                                    componentName: 'sampling-info-step',
                                    uniqueInstanceName: 'sampling-info', /* unique to step */
                                    parameters: {
                                        selectPhysThingData: "['select-project']['select-phys-thing']"
                                    },
                                },
                            ], 
                        },
                    ],
                },
                {
                    title: 'Image',
                    name: 'image-step',  /* unique to workflow */
                    required: true,
                    informationboxdata: {
                        heading: 'Image Services',
                        text: 'Image services provide you with picture(s) of an object, often from multiple vantage points, \
                        that can be annotated to indicate the location or region of an observation. \
                        If you wish, you can upload photographs and automatically create a new image service \
                        to document the location of your observations of an object',
                    },
                    layoutSections: [
                        {
                            sectionTitle: 'Image Service',
                            componentConfigs: [
                                { 
                                    componentName: 'sample-taking-image-step',
                                    uniqueInstanceName: 'image-service-instance', /* unique to step */
                                    tilesManaged: 'one',
                                    parameters: {
                                        graphid: '707cbd78-ca7a-11e9-990b-a4d18cec433a',  /* Digital Resources */
                                        physicalThingResourceId: "['select-project']['select-phys-thing']['physicalThing']",
                                        samplingInfoData: "['sample-info']['sampling-info']",
                                    },
                                },
                            ], 
                        },
                    ],
                },
                {
                    title: 'Sample Info',
                    name: 'sample-location-step', /* unique to workflow */
                    required: true,
                    workflowstepclass: 'analysis-areas-workflow-regions-step',
                    hiddenWorkflowButtons: ['undo', 'save'],
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'sample-taking-sample-location-step',
                                    uniqueInstanceName: 'sample-location-instance', /* unique to step */
                                    tilesManaged: 'one',
                                    parameters: {
                                        graphid: '9519cb4f-b25b-11e9-8c7b-a4d18cec433a',  /* physical thing */
                                        physicalThingResourceId: "['select-project']['select-phys-thing']['physicalThing']",
                                        physicalThingName: "['select-project']['select-phys-thing']['physThingName']",
                                        imageServiceInstanceData: "['image-step']['image-service-instance'][0]['data']",
                                        projectSet: "['select-project']['select-phys-thing']['projectSet']",
                                        samplingActivityResourceId: "['sample-info']['sampling-info']['samplingActivityResourceId']", 
                                    },
                                },
                            ], 
                        },
                    ],
                },
                {
                    title: 'Summary',
                    name: 'add-project-complete',  /* unique to workflow */
                    graphid: '0b9235d9-ca85-11e9-9fa2-a4d18cec433a',
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'sample-taking-final-step',
                                    uniqueInstanceName: 'sample-taking-final',
                                    parameters: {
                                        samplingActivityResourceId: "['sample-info']['sampling-info']['samplingActivityResourceId']",
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
        template: { require: 'text!templates/views/components/plugins/sample-taking-workflow.htm' }
    });
});
