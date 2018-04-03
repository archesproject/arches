define(['jquery', 'underscore', 'knockout-mapping', 'views/forms/base', 'views/forms/sections/branch-list'], function ($, _, koMapping, BaseForm, BranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);

            this.addBranchList(new BranchList({
                el: this.$el.find('#measurement-section')[0],
                data: this.data,
                dataKey: 'MEASUREMENTS.E16',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));
                      
        }
    });
});

