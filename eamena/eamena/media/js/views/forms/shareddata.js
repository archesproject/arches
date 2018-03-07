define(['jquery', 
    'underscore', 
    'knockout-mapping', 
    'views/forms/base', 
    'views/forms/sections/branch-list',
    'bootstrap-datetimepicker',], 
    function ($, _, koMapping, BaseForm, BranchList) {
        return BaseForm.extend({
            initialize: function() {
                BaseForm.prototype.initialize.apply(this);                
                
                var self = this;
                var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
                date_picker.on('dp.change', function(evt){
                    $(this).find('input').trigger('change'); 
                });


                this.addBranchList(new BranchList({
                    el: this.$el.find('#shared-appellation-section')[0],
                    data: this.data,
                    dataKey: 'SHARED_DATA_SOURCE_APPELLATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));

                this.addBranchList(new BranchList({
                    el: this.$el.find('#shared-affiliation-section')[0],
                    data: this.data,
                    dataKey: 'SHARED_DATA_SOURCE_AFFILIATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#shared-project-section')[0],
                    data: this.data,
                    dataKey: 'SHARED_DATA_SOURCE_CREATOR_APPELLATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));

                this.addBranchList(new BranchList({
                    el: this.$el.find('#shared-creation-date-section')[0],
                    data: this.data,
                    dataKey: 'SHARED_DATA_SOURCE_DATE_OF_CREATION.E50',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
            }
        });
    }
);