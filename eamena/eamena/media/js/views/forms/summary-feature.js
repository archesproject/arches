define(['jquery', 
    'summernote',
    'underscore', 
    'knockout-mapping', 
    'views/forms/base', 
    'views/forms/sections/branch-list',
    'views/forms/sections/validation',
    'bootstrap-datetimepicker',], 
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
                    el: this.$el.find('#names-section')[0],
                    data: this.data,
                    dataKey: 'NAME.E41',
                    validateBranch: function (nodes) {
                        var valid = true;
                        var primaryname_count = 0;
                        var primaryname_conceptid = this.viewModel.primaryname_conceptid;
                        _.each(nodes, function (node) {
                            if (node.entitytypeid === 'NAME.E41') {
                                if (node.value === ''){
                                    valid = false;
                                }
                            }
                            if (node.entitytypeid === 'NAME_TYPE.E55') {
                                if (node.value === primaryname_conceptid){
                                    _.each(self.viewModel['branch_lists'], function (branch_list) {
                                        _.each(branch_list.nodes, function (node) {
                                            if (node.entitytypeid === 'NAME_TYPE.E55' && node.value === primaryname_conceptid) {
                                                valid = false;
                                            }
                                        }, this);
                                    }, this);
                                }
                            }
                        }, this);
                        return valid;
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#classification-section')[0],
                    data: this.data,
                    dataKey: 'HERITAGE_CLASSIFICATION_TYPE.E55', 
                    rules: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#designation-section')[0],
                    data: this.data,
                    dataKey: 'RIGHT.E30', 
                    validateBranch: function (nodes) {
                        var ck0 = this.validateHasValues(nodes)
                        var ck1 = vt.isValidDate(nodes,'DESIGNATION_TO_DATE.E61');
                        var ck2 = vt.isValidDate(nodes,'DESIGNATION_FROM_DATE.E61');
                        return ck0 && ck1 && ck2;
                    }
                }));
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#description-section')[0],
                    data: this.data,
                    dataKey: 'DESCRIPTION_ASSIGNMENT.E13',
                    validateBranch: function(nodes){
                        return this.validateHasValues(nodes);
                    }
                }));
            }
        });
    }
);


$(function($) {
    PlusMinus = true;	
    $('#plusminus').click(function() {

        var wasPlay = $(this).hasClass('fa-plus-square');
        $(this).removeClass('fa-plus-square fa-minus-square');
        var klass = wasPlay ? 'fa-minus-square' : 'fa-plus-square';
        $(this).addClass(klass)
        if (PlusMinus == true) {
            $('#tobehidden').show();
        } else {
            $('#tobehidden').hide();
        }
        PlusMinus = !PlusMinus;
    }); 
    
});