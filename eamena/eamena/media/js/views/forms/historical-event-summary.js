define(['jquery', 'views/forms/base', 'views/forms/sections/branch-list', ], function ($, BaseForm, BranchList) {
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
                    el: this.$el.find('#begin-dates-section')[0],
                    data: this.data,
                    dataKey: 'BEGINNING_OF_EXISTENCE.E63',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));

                this.addBranchList(new BranchList({
                    el: this.$el.find('#end-dates-section')[0],
                    data: this.data,
                    dataKey: 'END_OF_EXISTENCE.E64',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));

                this.addBranchList(new BranchList({
                    el: this.$el.find('#keywords-section')[0],
                    data: this.data,
                    dataKey: 'KEYWORD.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
            }
        });
});


