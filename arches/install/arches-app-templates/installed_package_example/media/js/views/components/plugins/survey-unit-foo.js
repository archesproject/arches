define([
    'knockout',
    'jquery',
    'arches',
    'viewmodels/workflow',
    'viewmodels/workflow-step',
    'templates/views/components/plugins/survey-unit-foo.htm',
    'views/components/workflows/survey-unit-foo/project-area-overview-foo',
    'views/components/workflows/survey-unit-foo/survey-unit-final-foo',
], function(ko, $, arches, Workflow, WorkflowStep, SurveyUnitWorkflowTemplate) {
    return ko.components.register('survey-unit-foo', {
        viewModel: function(params) {
            var self = this;
            this.componentName = 'survey-unit-foo';

            this.selectedAddresses = ko.observable();
            this.selectedAddressesString = ko.computed(() => {
                if (self.selectedAddresses()) {
                    return self.selectedAddresses().join(', ');
                }
            });
            this.shouldShowCustomTitleBar = ko.computed(() => {
                return Boolean(this.selectedAddresses() && this.activeStep()['name'] !== 'project-area-overview');
            });

            this.stepConfig = [
                {
                    title: 'Survey Project Area Overview',
                    name: 'project-area-overview',  /* unique to workflow */
                    required: true,
                    workflowstepclass: 'survey-unit-project-area-overview-step',
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'project-area-overview-step',
                                    uniqueInstanceName: 'project-area-overview', /* unique to step */
                                    tilesManaged: 'none',
                                    selectedAddresses: self.selectedAddresses,
                                },
                            ],
                        },
                    ],
                },
                {
                    title: 'Take Photographs',
                    name: 'add-photographs',  /* unique to workflow */
                    // saveWithoutProgressing: true,
                    required: true,
                    workflowstepclass: 'survey-unit-project-photographs-step',
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'default-card',
                                    uniqueInstanceName: 'add-photographs', /* unique to step */
                                    componentType: 'card',
                                    parameters: {
                                        nodegroupid: 'aacb7723-e11d-11ec-bb77-e37ec032dc2b',
                                        graphid: 'aacb7716-e11d-11ec-bb77-e37ec032dc2b',
                                        resourceid: "['project-area-overview']['project-area-overview']['resourceInstanceId']",
                                        hiddenNodes: ["0e4b00e0-23db-11ed-bb77-e37ec032dc2b"]
                                    },
                                },
                            ],
                        },
                    ],
                },
                {
                    title: 'Details & Status',
                    name: 'details-and-status',  /* unique to workflow */
                    // saveWithoutProgressing: true,
                    required: true,
                    workflowstepclass: 'alteration-step',
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'default-card',
                                    uniqueInstanceName: 'describe-alterations', /* unique to step */
                                    componentType: 'card',
                                    parameters: {
                                        nodegroupid: 'aacb7720-e11d-11ec-bb77-e37ec032dc2b',
                                        graphid: 'aacb7716-e11d-11ec-bb77-e37ec032dc2b',
                                        resourceid: "['project-area-overview']['project-area-overview']['resourceInstanceId']",
                                        hiddenNodes: [
                                            'aacb77a9-e11d-11ec-bb77-e37ec032dc2b',
                                            'aacb7788-e11d-11ec-bb77-e37ec032dc2b'
                                        ],
                                    },
                                },
                                { 
                                    componentName: 'default-card',
                                    uniqueInstanceName: 'field-notes', /* unique to step */
                                    componentType: 'card',
                                    parameters: {
                                        nodegroupid: 'aacb7741-e11d-11ec-bb77-e37ec032dc2b',
                                        graphid: 'aacb7716-e11d-11ec-bb77-e37ec032dc2b',
                                        resourceid: "['project-area-overview']['project-area-overview']['resourceInstanceId']",
                                        hiddenNodes: [
                                            'aacb778d-e11d-11ec-bb77-e37ec032dc2b'
                                        ]
                                    },
                                },
                                { 
                                    componentName: 'default-card',
                                    uniqueInstanceName: 'unit-status', /* unique to step */
                                    componentType: 'card',
                                    parameters: {
                                        nodegroupid: 'aacb773b-e11d-11ec-bb77-e37ec032dc2b',
                                        graphid: 'aacb7716-e11d-11ec-bb77-e37ec032dc2b',
                                        resourceid: "['project-area-overview']['project-area-overview']['resourceInstanceId']",
                                        hiddenNodes: [
                                            'aacb7792-e11d-11ec-bb77-e37ec032dc2b'
                                        ]
                                    },
                                },
                            ],
                        },
                    ],
                },
                {
                    title: 'Summary',
                    name: 'survey-workflow-complete',  /* unique to workflow */
                    description: 'Summary',
                    workflowstepclass: 'survey-unit-project-summary-step',
                    layoutSections: [
                        {
                            componentConfigs: [
                                { 
                                    componentName: 'survey-unit-final-step',
                                    uniqueInstanceName: 'survey-unit-final',
                                    tilesManaged: 'none',
                                    parameters: {
                                        photos: "['add-photographs']['add-photographs']",
                                        description: "['describe-unit']['describe-unit']",
                                        alterations: "['describe-alterations']['describe-alterations']",
                                        notes: "['field-notes']['field-notes']",
                                        status: "['unit-status']['unit-status']",
                                        parcelResourceId: "['project-area-overview']['project-area-overview']['resourceInstanceId']"
                                    },
                                },
                            ], 
                        },
                    ],
                }
            ];

            Workflow.apply(this, [params]);

            self.activeStep.subscribe(step => {
                if (step['name'] !== "project-area-overview") {  // only fire on transition from first step to second
                    const selectedAddresses = self.getDataFromComponentPath("['project-area-overview']['project-area-overview']['selectedAddresses']");
                    if (selectedAddresses) { self.selectedAddresses(selectedAddresses); }
                }
            });
        },
        template: SurveyUnitWorkflowTemplate
    });
});