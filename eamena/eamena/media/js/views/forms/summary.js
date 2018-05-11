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
                        return this.validateHasValues(nodes);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#classification-section')[0],
                    data: this.data,
                    dataKey: 'HERITAGE_RESOURCE_GROUP_TYPE.E55', 
                    rules: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#designation-section')[0],
                    data: this.data,
                    dataKey: 'RIGHT_NEW.E30', 
                    validateBranch: function (nodes) {
                        var ck0 = this.validateHasValues(nodes);
                        var ck1 = vt.isValidDate(nodes, 'DESIGNATION_FROM_DATE.E61');
                        var ck2 = vt.isValidDate(nodes, 'DESIGNATION_TO_DATE.E61');
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