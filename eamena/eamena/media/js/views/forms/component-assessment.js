define(['jquery', 
    'summernote',
    'underscore', 
    'knockout-mapping', 
    'views/forms/base', 
    'views/forms/sections/branch-list',
    'views/forms/sections/location-branch-list',
    'views/forms/sections/validation',
    'bootstrap-datetimepicker',
    ], 
    function ($, summernote, _, koMapping, BaseForm, BranchList, LocationBranchList, ValidationTools) {
        var vt = new ValidationTools;
        return BaseForm.extend({
            initialize: function() {
                BaseForm.prototype.initialize.apply(this);                
                var self = this;
                console.log("self.data", self.data);
                var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
                date_picker.on('dp.change', function(evt){
                    $(this).find('input').trigger('change'); 
                });

                this.addBranchList(new BranchList({
                    el: this.$el.find('#investigation-section')[0],
                    data: this.data,
                    dataKey: 'INVESTIGATION_ACTIVITY.E7',
                    validateBranch: function (nodes) {
                        var ck0 = this.validateHasValues(nodes);
                        var ck1 = vt.isValidDate(nodes,"INVESTIGATION_DATE_OF_ACTIVITY.E49");
                        return ck0 && ck1;
                    }
                }));
                
            }
        });
    }
);