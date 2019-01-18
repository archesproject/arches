define(['jquery', 
    'underscore', 
    'knockout',
    'views/forms/wizard-base', 
    'views/forms/sections/branch-list',
    'views/forms/sections/validation',
    'bootstrap-datetimepicker',
    'summernote'], function ($, _, ko, WizardBase, BranchList, ValidationTools, datetimepicker, summernote) {
    var vt = new ValidationTools;
    return WizardBase.extend({
        initialize: function() {
            WizardBase.prototype.initialize.apply(this);

            var self = this;
            var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});            
            this.getBlankFormData();
            date_picker.on('dp.change', function(evt){
                $(this).find('input').trigger('change'); 
            });
            self.startWorkflow();
            console.log('started workflow');
            console.log(this.branchLists);
            console.log(this.data);
            
            // step 1
            this.addBranchList(new BranchList({
                el: this.$el.find('#disturbances-section')[0],
                data: this.data,
                dataKey: 'DAMAGE_STATE.E3',
                validateBranch: function (nodes) {
                    var ck0 = vt.isValidDate(nodes,"DISTURBANCE_CAUSE_DATE_TO.E61");
                    var ck1 = vt.isValidDate(nodes,"DISTURBANCE_CAUSE_DATE_FROM.E61");
                    var ck2 = vt.isValidDate(nodes,"DISTURBANCE_CAUSE_DATE_OCCURRED_ON.E61");
                    var ck3 = vt.isValidDate(nodes,"DISTURBANCE_CAUSE_DATE_OCCURRED_BEFORE.E61");
                    var ck4 = vt.nodesHaveValues(nodes, {"mustBeFilled":["DISTURBANCE_CAUSE_CATEGORY_TYPE.E55"]});
                    return ck0 && ck1 && ck2 && ck3 && ck4
                }
            }));

            
            // step 3
            this.addBranchList(new BranchList({
                el: this.$el.find('#potential-section')[0],
                data: this.data,
                dataKey: 'THREAT_INFERENCE_MAKING.I5',
                validateBranch: function (nodes) {
                   return vt.mustHaveAtLeastOne(nodes)
                }
            }));

            // step 4
            this.addBranchList(new BranchList({
                el: this.$el.find('#recommendation-section')[0],
                data: this.data,
                dataKey: 'ACTIVITY_PLAN.E100',
                validateBranch: function (nodes) {
                    return vt.mustHaveAtLeastOne(nodes)
                },
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#priority-section')[0],
                data: this.data,
                dataKey: 'ACTIVITY_PLAN_PRIORITY_ASSIGNMENT.E13',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                },
            }));
            

            this.listenTo(this,'change', this.dateEdit)
            
            this.events['click .disturbance-date-item'] = 'showDate';
            this.events['click .disturbance-date-edit'] = 'dateEdit';
        },
        
        
        dateEdit: function (e, b) {
            _.each(b.nodes(), function (node) {
                if (node.entitytypeid() == 'DISTURBANCE_CAUSE_DATE_FROM.E61' && node.value() && node.value() != '') {
                    $('.div-date').addClass('hidden')
                    $('.div-date-from-to').removeClass('hidden')
                    $('.disturbance-date-value').html('From-To')
                } else if (node.entitytypeid() == 'DISTURBANCE_CAUSE_DATE_OCCURRED_ON.E61' && node.value() && node.value() != '') {
                    $('.div-date').addClass('hidden')
                    $('.div-date-on').removeClass('hidden')
                    $('.disturbance-date-value').html('On')
                } else if (node.entitytypeid() == 'DISTURBANCE_CAUSE_DATE_OCCURRED_BEFORE.E61' && node.value() && node.value() != '') {
                    $('.div-date').addClass('hidden')
                    $('.div-date-before').removeClass('hidden')
                    $('.disturbance-date-value').html('Before')
                }
            })
        },
        
        
        showDate: function (e) {
            $('.div-date').addClass('hidden')
            $('.disturbance-date-value').html($(e.target).html())
            if ($(e.target).hasClass("disturbance-date-from-to")) {
                $('.div-date-from-to').removeClass('hidden')
            } else if ($(e.target).hasClass("disturbance-date-on")) {
                $('.div-date-on').removeClass('hidden')
            } else if ($(e.target).hasClass("disturbance-date-before")) {
                $('.div-date-before').removeClass('hidden')
            }
        },

        startWorkflow: function() {
            
            this.switchBranchForEdit();
        },

        switchBranchForEdit: function(branchData){
            this.prepareData(branchData);

            _.each(this.branchLists, function(branchlist){
                branchlist.data = branchData;
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
                
                // step 1
                'TEST': {
                    'branch_lists':[]
                },
                
                // step 2
                'CONDITION_ASSESSMENT_IMAGE.E38': {
                    'branch_lists':[]
                },
                
                // step 3
                'THREAT_INFERENCE_MAKING.I5': {
                    'branch_lists':[]
                },

                //step 4
                'ACTIVITY_PLAN.E100': {
                    'branch_lists':[]
                },
                'ACTIVITY_PLAN_PRIORITY_ASSIGNMENT.E13': {
                    'branch_lists':[]
                },
            })
        },
        cancelWorkflow: function() { 
            this.cancel(); 
        },

    });
});