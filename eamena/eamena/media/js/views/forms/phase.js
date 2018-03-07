define(['jquery', 'underscore', 'knockout-mapping', 'views/forms/base', 'views/forms/sections/branch-list'], function ($, _, koMapping, BaseForm, BranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);

            var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
            date_picker.on('dp.change', function(evt){
                $(this).find('input').trigger('change'); 
            });

            this.addBranchList(new BranchList({
                el: this.$el.find('#phase-section')[0],
                data: this.data,
                dataKey: 'PHASE_TYPE_ASSIGNMENT.E17',
                validateBranch: function (nodes) {
                    var valid = true;
                    _.each(nodes, function (node) {
                        if (node.entitytypeid === 'HISTORICAL_EVENT_TYPE.E55') {
                            if (node.value === ''){
                                valid = false;
                            }
                        }
                    }, this);
                    return valid;
                }
            }));
        }
    });
});

