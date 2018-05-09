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
                    el: this.$el.find('#classification-section')[0],
                    data: this.data,
                    dataKey: 'COMPONENT_CLASSIFICATION.E17',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes)
                    }
                }));
                
            }
        });
    }
);