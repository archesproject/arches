define(['jquery', 
    'summernote',
    'underscore', 
    'knockout-mapping', 
    'views/forms/base', 
    'views/forms/sections/branch-list',
    'views/forms/sections/validation',
    'bootstrap-datetimepicker',
    ], 
    function ($, summernote, _, koMapping, BaseForm, BranchList, ValidationTools) {
        var vt = new ValidationTools;
        return BaseForm.extend({
            initialize: function() {
                
                BaseForm.prototype.initialize.apply(this);                
                var self = this;
                var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
                date_picker.on('dp.change', function(evt){
                    $(this).find('input').trigger('change'); 
                });

                this.addBranchList(new BranchList({
                    el: this.$el.find('#investigator-name-section')[0],
                    data: this.data,
                    dataKey: 'INVESTIGATION_ASSESSMENT_ACTIVITY.E7',
                    validateBranch: function (nodes) {
                        var ck0 = true;
                        var primaryname_count = 0;
                        var primaryname_conceptid = this.viewModel.primaryname_conceptid;
                        _.each(nodes, function (node) {
                            if (node.entitytypeid === 'INVESTIGATOR_NAME.E41') {
                                if (node.value === ''){
                                    ck0 = false;
                                }
                            }
                            if (node.entitytypeid === 'INVESTIGATOR_ROLE_TYPE.E55') {
                                if (node.value === primaryname_conceptid){
                                    _.each(self.viewModel['branch_lists'], function (branch_list) {
                                        _.each(branch_list.nodes, function (node) {
                                            if (node.entitytypeid === 'INVESTIGATOR_ROLE_TYPE.E55' && node.value === primaryname_conceptid) {
                                                ck0 = false;
                                            }
                                        }, this);
                                    }, this);
                                }
                            }
                        }, this);
                        var ck1 = this.validateHasValues(nodes)
                        var ck2 = vt.isValidDate(nodes,'ASSESSMENT_ACTIVITY_DATE.E49');
                        return ck0 && ck1 && ck2;
                    }
                }));
            }
        });
    }
);