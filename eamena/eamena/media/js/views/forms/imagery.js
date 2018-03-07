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
                    el: this.$el.find('#imagery-creation-section')[0],
                    data: this.data,
                    dataKey: 'IMAGERY_CREATOR_APPELLATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#acquisition-section')[0],
                    data: this.data,
                    dataKey: 'ACQUISITION_ASSIGNMENT.E17',
                    validateBranch: function (nodes) {
                        return true;                        
                        return this.validateHasValues(nodes);
                    }
                }));
                                   
                this.addBranchList(new BranchList({
                    el: this.$el.find('#acquisition-date-section')[0],
                    data: this.data,
                    dataKey: 'DATE_OF_ACQUISITION.E50',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                     
                this.addBranchList(new BranchList({
                    el: this.$el.find('#publication-date-section')[0],
                    data: this.data,
                    dataKey: 'IMAGERY_DATE_OF_PUBLICATION.E50',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));

                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#catalogue-ID-section')[0],
                    data: this.data,
                    dataKey: 'CATALOGUE_ID.E42',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
        
         
                this.addBranchList(new BranchList({
                    el: this.$el.find('#resolution-section')[0],
                    data: this.data,
                    dataKey: 'IMAGERY_SAMPLED_RESOLUTION_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));

                this.addBranchList(new BranchList({
                    el: this.$el.find('#processing-section')[0],
                    data: this.data,
                    dataKey: 'PROCESSING_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#rights-section')[0],
                    data: this.data,
                    dataKey: 'RIGHT_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#imagery-source-type-section')[0],
                    data: this.data,
                    dataKey: 'IMAGERY_SOURCE_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
            }
        });
    }
);