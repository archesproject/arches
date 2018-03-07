define(['jquery', 'views/forms/base', 'views/forms/sections/branch-list', ], function ($, BaseForm, BranchList) {
        return BaseForm.extend({
            initialize: function() {
                BaseForm.prototype.initialize.apply(this);                
                var self = this;


                this.addBranchList(new BranchList({
                    el: this.$el.find('#formats-section')[0],
                    data: this.data,
                    dataKey: 'INFORMATION_CARRIER.E84',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
         
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#info-resource-type-section')[0],
                    data: this.data,
                    dataKey: 'INFORMATION_RESOURCE_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));                               

            }
        });
});


