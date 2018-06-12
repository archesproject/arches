define(['jquery', 
    'underscore', 
    'knockout',
    'views/forms/wizard-base', 
    'views/forms/sections/branch-list',
    'views/forms/sections/location-branch-list',
    'bootstrap-datetimepicker',
    'summernote','views/forms/sections/validation',], function ($, _, ko, WizardBase, BranchList, LocationBranchList, datetimepicker, summernote, ValidationTools) {
        var vt = new ValidationTools;
        return WizardBase.extend({
            initialize: function() {
                WizardBase.prototype.initialize.apply(this);
    
                var self = this;
                var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
                date_picker.on('dp.change', function(evt){
                    $(this).find('input').trigger('change'); 
                });            
                var currentEdited = this.getBlankFormData();
                var locationBranchList = new LocationBranchList({
                    el: this.$el.find('#heritage-location')[0],
                    data: this.data,
                    dataKey: 'GEOMETRIC_PLACE_EXPRESSION.SP5',
                    addParentGeom: true
                });
                this.addBranchList(locationBranchList);
    
            
                var relationBranchList = new BranchList({
                    el: this.$el.find('#relation-list')[0],
                    data: this.data,
                    dataKey: 'related-resources',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    },
                    addBlankEditBranch: function(){
                        return null;
                    },
                    getEditedBranchTypeInfo: function() {
                        if (!this.getEditedBranch()) {
                            return {};
                        }
                        return resourceTypes[this.getEditedBranch().relatedresourcetype()];
                    }
                });
    
                this.addBranchList(relationBranchList);
            
                this.addBranchList(new BranchList({
                    el: this.$el.find('#feature-names')[0],
                    data: this.data,
                    dataKey: 'NAME.E41',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#feature-classification')[0],
                    data: this.data,
                    dataKey: 'HERITAGE_CLASSIFICATION_TYPE.E55',
                    requiredBranch: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));            
                this.addBranchList(new BranchList({
                    el: this.$el.find('#feature-use')[0],
                    data: this.data,
                    dataKey: 'HERITAGE_FEATURE_USE_TYPE.E55',
                    requiredBranch: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));            
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#assessment-summary')[0],
                    data: this.data,
                    dataKey: 'INVESTIGATION_ASSESSMENT_ACTIVITY.E7',
                    requiredBranch: true,
                    validateBranch: function (nodes) {
                        var canBeEmpty = ['INVESTIGATOR_ROLE_TYPE.E55']
                        var ck1 = this.validateHasValues(nodes, canBeEmpty)
                        var ck2 = vt.isValidDate(nodes,'ASSESSMENT_ACTIVITY_DATE.E49');
                        return ck1 && ck2;
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#remarks-assignment')[0],
                    data: this.data,
                    dataKey: 'CONDITION_REMARKS_ASSIGNMENT.E13',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#priority-assignment')[0],
                    data: this.data,
                    dataKey: 'OVERALL_PRIORITY_ASSIGNMENT.E13',
                    requiredBranch: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#overall-condition')[0],
                    data: this.data,
                    dataKey: 'OVERALL_CONDITION_TYPE.E55',
                    requiredBranch: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#relationship-assignment')[0],
                    data: this.data,
                    dataKey: 'related-resources',
                    requiredBranch: true
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
                    'GEOMETRIC_PLACE_EXPRESSION.SP5': {
                         'branch_lists':[]
                    },
                    'NAME.E41': {
                        'branch_lists': []
                    },
                    'HERITAGE_CLASSIFICATION_TYPE.E55': {
                        'branch_lists': []
                    },                
                    'HERITAGE_FEATURE_USE_TYPE.E55': {
                        'branch_lists': []
                    },                                
                    'INVESTIGATION_ASSESSMENT_ACTIVITY.E7': {
                        'branch_lists':[]
                    },
                    'related-resources': {
                        'branch_lists':[]
                    },
                    'CONDITION_REMARKS_ASSIGNMENT.E13': {
                         'branch_lists': []
                    },        
                    'OVERALL_PRIORITY_ASSIGNMENT.E13': {
                         'branch_lists': []
                    },            
                    'OVERALL_CONDITION_TYPE.E55': {
                         'branch_lists': []
                    }                  
                })
            }
    
        });
});
$(function($) {
    $('#relation-type').on('change', function() {
        $('#end-workflow').removeClass('disabled');
    });   
});