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
            var currentEditedClassification = this.getBlankFormData();

            date_picker.on('dp.change', function(evt){
                $(this).find('input').trigger('change'); 
            });

            // this.editAssessment = function(branchlist){
            //     self.switchBranchForEdit(branchlist);
            // }

            this.deleteAssessment = function(branchlist){
                self.deleteClicked(branchlist);
            }

            ko.applyBindings(this, this.$el.find('#existing-classifications')[0]);

            this.addBranchList(new BranchList({
                el: this.$el.find('#resource-type-section')[0],
                data: this.data,
                dataKey: 'SITE_MORPHOLOGY_TYPE.E55',
                singleEdit: true
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#related-features-section')[0],
                data: this.data,
                dataKey: 'SITE_OVERALL_SHAPE_TYPE.E55'
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#to-date-section')[0],
                data: currentEditedClassification,
                dataKey: 'TO_DATE.E49',
                singleEdit: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));   
            this.addBranchList(new BranchList({
                el: this.$el.find('#from-date-section')[0],
                data: currentEditedClassification,
                dataKey: 'FROM_DATE.E49',
                singleEdit: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            })); 
            
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
                'SITE_MORPHOLOGY_TYPE.E55': {
                    'branch_lists':[]
                },
                'SITE_OVERALL_SHAPE_TYPE.E55': {
                    'branch_lists':[]
                },
                'FROM_DATE.E49': {
                    'branch_lists': []
                },
                'TO_DATE.E49': {
                    'branch_lists': []
                },        
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