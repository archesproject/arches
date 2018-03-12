define(['jquery', 
    'underscore', 
    'knockout',
    'views/forms/wizard-base', 
    'views/forms/sections/branch-list',
    'bootstrap-datetimepicker',
    'summernote'], function ($, _, ko, WizardBase, BranchList, datetimepicker, summernote) {

    return WizardBase.extend({
        initialize: function() {
            WizardBase.prototype.initialize.apply(this);

            var self = this;
            var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});            
            var currentEdited = this.getBlankFormData();
            console.log("this.data", this.data);
            // date_picker.on('dp.change', function(evt){
            //     $(this).find('input').trigger('change'); 
            // });

            // this.editAssessment = function(branchlist){
            //     self.switchBranchForEdit(branchlist);
            // }

            // this.deleteAssessment = function(branchlist){
            //     self.deleteClicked(branchlist);
            // }

            // ko.applyBindings(this, this.$el.find('#existing')[0]);

        
            var relationBranchList = new BranchList({
                el: this.$el.find('.relation-list')[0],
                data: this.data,
                dataKey: 'related-resources',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                },
                addBlankEditBranch: function(){
                    return null;
                },
                // getData: function(){
                //     var data = koMapping.toJS(this.viewModel.branch_lists());
                //     _.each(data, function(item){
                //         var i = item;
                //         delete item.editing;
                //     }, this); 
                //     return data;
                // },
                getEditedBranchTypeInfo: function() {
                    if (!this.getEditedBranch()) {
                        return {};
                    }
                    return resourceTypes[this.getEditedBranch().relatedresourcetype()];
                }
            });

            this.addBranchList(relationBranchList);
        
            this.addBranchList(new BranchList({
                el: this.$el.find('#heritage-classification')[0],
                data: this.data,
                dataKey: 'NAME.E41',
                singleEdit: true
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#assessment-summary')[0],
                data: this.data,
                dataKey: 'INVESTIGATION_ASSESSMENT_ACTIVITY.E7',
                singleEdit: true
            }));
            
            $('#end-workflow').removeClass('disabled');      
        },

        startWorkflow: function() { 
            this.switchBranchForEdit(this.getBlankFormData());
        },
        
        switchBranchForEdit: function(classificationData){
            this.prepareData(classificationData);
        
            _.each(this.branchLists, function(branchlist){
                branchlist.data = classificationData;
                branchlist.undoAllEdits();
            }, this);
        
            this.toggleEditor();
        },

        prepareData: function(assessmentNode){
            _.each(assessmentNode, function(value, key, list){
                assessmentNode[key].domains = this.data.domains;
            }, this);
            return assessmentNode;
        },

        getBlankFormData: function(){
            return this.prepareData({
                // 'SITE_MORPHOLOGY_TYPE.E55': {
                //     'branch_lists':[]
                // },
                'NAME.E41': {
                    'branch_lists': []
                },
                'INVESTIGATION_ASSESSMENT_ACTIVITY.E7': {
                    'branch_lists':[]
                },
                'related-resources': {
                    'branch_lists':[]
                },
                // 'TO_DATE.E49': {
                //     'branch_lists': []
                // },        
            })
        },

        // deleteClicked: function(branchlist) {
        //     var warningtext = '';
        // 
        //     this.deleted_assessment = branchlist;
        //     this.confirm_delete_modal = this.$el.find('.confirm-delete-modal');
        //     this.confirm_delete_modal_yes = this.confirm_delete_modal.find('.confirm-delete-yes');
        //     this.confirm_delete_modal_yes.removeAttr('disabled');
        // 
        //     warningtext = this.confirm_delete_modal.find('.modal-body [name="warning-text"]').text();
        //     this.confirm_delete_modal.find('.modal-body [name="warning-text"]').text(warningtext + ' ' + branchlist['SITE_MORPHOLOGY_TYPE.E55'].branch_lists[0].nodes[0].label);           
        //     this.confirm_delete_modal.modal('show');
        // }

    });
});