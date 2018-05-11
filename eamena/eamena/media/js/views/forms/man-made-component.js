define(['jquery', 
    'underscore', 
    'knockout',
    'views/forms/wizard-base', 
    'views/forms/sections/branch-list',
    'views/forms/sections/location-branch-list',
    'bootstrap-datetimepicker',
    'summernote'], function ($, _, ko, WizardBase, BranchList, LocationBranchList, datetimepicker, summernote) {

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
                dataKey: 'SPATIAL_COORDINATES.E47'
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
                el: this.$el.find('#classification-section')[0],
                data: this.data,
                dataKey: 'COMPONENT_CLASSIFICATION.E17'
            }));            
            this.addBranchList(new BranchList({
                el: this.$el.find('#investigation-section')[0],
                data: this.data,
                dataKey: 'INVESTIGATION_ACTIVITY.E7'
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#relationship-assignment')[0],
                data: this.data,
                dataKey: 'related-resources',
                requiredBranch: true,
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
                'SPATIAL_COORDINATES.E47': {
                     'branch_lists':[]
                },
                'COMPONENT_CLASSIFICATION.E17': {
                    'branch_lists': []
                },
                'related-resources': {
                    'branch_lists':[]
                },
                'INVESTIGATION_ACTIVITY.E7': {
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