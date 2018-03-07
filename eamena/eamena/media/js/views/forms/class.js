 define(['jquery', 'underscore', 'knockout-mapping', 'views/forms/base', 'views/forms/sections/branch-list'], function ($, _, koMapping, BaseForm, BranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);

            this.addBranchList(new BranchList({
                el: this.$el.find('#feature-section')[0],
                data: this.data,
                dataKey: 'FEATURE_EVIDENCE_ASSIGNMENT.E17',
                rules: true,
                validateBranch: function (nodes) {                       
                    return this.validateHasValues(nodes);
                }
            }));
                           
            this.addBranchList(new BranchList({
                el: this.$el.find('#interpretation-section')[0],
                data: this.data,
                dataKey: 'FEATURE_EVIDENCE_INTERPRETATION_ASSIGNMENT.E17',
                rules: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));
                           
        }
    });
});

