define(['jquery', 'underscore', 'knockout', 'arches', 'viewmodels/tabbed-report', 'utils/resource'], function($, _, ko, arches, TabbedReportViewModel, resourceUtils) {
    return ko.components.register('visual-work-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            TabbedReportViewModel.apply(this, [params]);

            if (params.summary) {

                this.editorLink = arches.urls.resource_editor + this.report.attributes.resourceid;

                var StatementTextId = 'e58ecc2e-c062-11e9-ba30-a4d18cec433a'; // ok
                var TypeOfWorkId = '28a4ae07-c062-11e9-a11d-a4d18cec433a';
                var DepictsPhysicalId = '5513933a-c062-11e9-9e4b-a4d18cec433a';

                /* created by is not available from the model
                var createById = '';
                this.createBy = ko.observableArray([]);
                this.createByObjs = resourceUtils.getNodeValues({
                    nodeId: createById,
                    returnTiles: false
                }, this.report.get('tiles'), this.report.graph);

                this.createByObjs.forEach(function(createByObj) {
                    if (createByObj) {
                        resourceUtils.lookupResourceInstanceData(createByObj.resourceId)
                            .then(function(data) {
                                self.createBy.push({ name: data._source.displayname, link: arches.urls.resource_report + createByObj.resourceId });
                            });
                    }});
                */

                var descriptionConceptValueId = 'df8e4cf6-9b0b-472f-8986-83d5b2ca28a0';
                var statementTextId = 'e58ecc2e-c062-11e9-ba30-a4d18cec433a';
                var statementTypeId = 'e58eb7b5-c062-11e9-b08d-a4d18cec433a';
                this.description = resourceUtils.getNodeValues({
                    nodeId: statementTextId,
                    //widgetLabel: 'Brief Text or Statement.Statement Text',
                    where: {
                        nodeId: statementTypeId,
                        //widgetLabel: 'Brief Text or Statement.Type of Statement',
                        contains: descriptionConceptValueId
                    },
                    returnTiles: false
                }, this.report.get('tiles'), this.report.graph);

                this.DepictsPhysicalValue = resourceUtils.getNodeValues({
                    nodeId: DepictsPhysicalId,
                    returnTiles: false
                }, this.report.get('tiles'), this.report.graph);

                this.depictsPhysicalName = ko.observableArray([]);
                this.DepictsPhysicalValue.forEach(function(depictsPhysical) {
                    if (depictsPhysical) {
                        resourceUtils.lookupResourceInstanceData(depictsPhysical.resourceId)
                            .then(function(data) {
                                self.depictsPhysicalName.push({ name: data._source.displayname, link: arches.urls.resource_report + depictsPhysical.resourceId });
                            });
                    }});

                this.TypeOfWorkName = ko.observable();

                this.TypeOfWorkValue = resourceUtils.getNodeValues({
                    nodeId: TypeOfWorkId,
                    returnTiles: false
                }, this.report.get('tiles'), this.report.graph);

                if (this.TypeOfWorkValue.length) {
                    $.ajax(arches.urls.concept_value + '?valueid=' + self.TypeOfWorkValue, {
                        dataType: "json"
                    }).done(function(data) {
                        self.TypeOfWorkName(data.value);
                    });
                }
            }
        },
        template: { require: 'text!templates/views/components/reports/visual-work.htm' }
    });
});
