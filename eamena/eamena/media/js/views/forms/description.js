define(['jquery', 'summernote', 'views/forms/base', 'views/forms/sections/branch-list', ], function ($, summernote, BaseForm, BranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);

            this.addBranchList(new BranchList({
                el: this.$el.find('#description-section')[0],
                data: this.data,
                dataKey: 'DESCRIPTION.E62',
                validateBranch: function(nodes){
                    return this.validateHasValues(nodes);
                }

            }));
        }
    });
});