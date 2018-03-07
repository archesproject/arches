define(['jquery', 'underscore', 'knockout-mapping', 'views/forms/base', 'views/forms/sections/branch-list'], function ($, _, koMapping, BaseForm, BranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);

            var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
            date_picker.on('dp.change', function(evt){
                $(this).find('input').trigger('change'); 
            });

            this.addBranchList(new BranchList({
                el: this.$el.find('#designation-section')[0],
                data: this.data,
                dataKey: 'PROTECTION_EVENT.E65',
                 validateBranch: function (nodes) {
                      return true;
                      return this.validateHasValues(nodes);
                 }
            }));
        }
    });
});