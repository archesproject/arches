define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'utils/report',
    'views/components/workflows/summary-step',
    'templates/views/components/workflows/survey-unit-workflow/survey-unit-final-step.htm'
], function(_, $, arches, ko, koMapping, reportUtils, SummaryStep, SurveyUnitFinalStepTemplate) {
    function viewModel(params) {
        var self = this;
        _.extend(this, params);
        params.form.resourceId(ko.unwrap(params.parcelResourceId));

        SummaryStep.apply(this, [params]);
        Object.assign(self, reportUtils);

        this.previous = () => {
            $('.tabbed-workflow-footer-button-container .btn.btn-primary').click();
        }

        this.resourceInstance = ko.observable();
        this.description = {
            windowType: {
                name: "Window Type(s)",
                value: ko.observable(),
            },
            claddingTypes: {
                name: "Cladding Type(s)",
                value: ko.observable(),
            },
        };

        this.alterations = {
            level: {
                name: "Level of Alteration"
            },
            type: {
                name: "Alteration Type"
            },
            data: ko.observableArray()
        };


        this.notes = {
            type: {
                name: "Note Type(s)",
            },
            description: {
                name: "Description",
            },
            date: {
                name: "Note Date",
            },
            data: ko.observableArray()
        };

        this.status = {
            unit: {
                name: "Unit Status"
            },
            date: {
                name: "Unit Status Date"
            },
            data: ko.observableArray()
        };

        this.photos = {
            source: {
                name: "Photo Source",
            },
            detail: {
                name: "Detail Photographs",
            },
            oblique: {
                name: "Oblique View Photographs",
            },
            straightOn: {
                name: "Straight-On Photographs",
            },
            date: {
                name: "Date of Photograph(s)",
            },
            data: ko.observableArray()
        };

        this.getResourceData(params.form.resourceId(), this.resourceInstance);

        this.resourceInstance.subscribe(x => {
            const descriptionNode = self.getRawNodeValue(x, 'resource', 'unit - physical description');
            self.description.windowType.value(self.getNodeValue(descriptionNode, 'windows', 'window type(s)'));
            self.description.claddingTypes.value(self.getNodeValue(descriptionNode, 'cladding', 'cladding type(s)'));

            const alterationsNode = self.getRawNodeValue(x, 'resource', 'alteration(s)');

            if(Array.isArray(alterationsNode)){
                self.alterations.data(alterationsNode.map(alteration => {
                    return { 
                        // "type": self.getNodeValue(alteration, 'alteration type'),
                        "level": self.getNodeValue(alteration, 'level of alteration')
                    };
                }));
            }

            const notesNode = self.getRawNodeValue(x, 'resource', 'note(s)');

            if(Array.isArray(notesNode)) {
                self.notes.data(notesNode.map(notes => {
                    return { 
                        type: self.getNodeValue(notes, 'note type(s)'),
                        date: self.getNodeValue(notes, 'note creation', 'note time-span', 'note date'),
                        // description: self.getNodeValue(notes, 'description'),
                    };
                }));
            }

            const statusNode = self.getRawNodeValue(x, 'resource', 'survey status');
            self.status.data({ 
                unit: self.getNodeValue(statusNode, 'unit status'),
            });

            const photoNodes = self.getRawNodeValue(x, 'resource', 'photograph(s)');

            self.photos.data(photoNodes.map(photoNode => {
                const detail = self.getFileUrls(self.getRawNodeValue(photoNode, 'detail photographs'));
                const oblique = self.getFileUrls(self.getRawNodeValue(photoNode, 'oblique view photographs'));
                const straightOn = self.getFileUrls(self.getRawNodeValue(photoNode, 'straight-on photographs'));
                const date = self.getNodeValue(photoNode, 'creation - date of photographs', 'photograph creation timespan', 'date of photograph(s)');
                return {
                    date, straightOn, oblique, detail
                };
            }));

        });
    }

    ko.components.register('survey-unit-final-step', {
        viewModel: viewModel,
        template: SurveyUnitFinalStepTemplate
    });
    return viewModel;
});