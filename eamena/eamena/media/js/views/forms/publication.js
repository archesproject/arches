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
                    el: this.$el.find('#titles-section')[0],
                    data: this.data,
                    dataKey: 'TITLE.E41',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
        
                this.addBranchList(new BranchList({
                    el: this.$el.find('#creator-section')[0],
                    data: this.data,
                    dataKey: 'CREATOR_APPELLATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#editor-section')[0],
                    data: this.data,
                    dataKey: 'EDITOR_APPELLATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#source-section')[0],
                    data: this.data,
                    dataKey: 'SOURCE_APPELLATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#place-section')[0],
                    data: this.data,
                    dataKey: 'BIBLIO_PLACE_APPELLATION.E44',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#publisher-section')[0],
                    data: this.data,
                    dataKey: 'PUBLISHER_APPELLATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
         
                this.addBranchList(new BranchList({
                    el: this.$el.find('#volume-section')[0],
                    data: this.data,
                    dataKey: 'VOLUME.E62',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#issue-section')[0],
                    data: this.data,
                    dataKey: 'ISSUE.E62',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               

                this.addBranchList(new BranchList({
                    el: this.$el.find('#pages-section')[0],
                    data: this.data,
                    dataKey: 'PAGES.E62',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               

                this.addBranchList(new BranchList({
                    el: this.$el.find('#figure-section')[0],
                    data: this.data,
                    dataKey: 'FIGURE.E62',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));

                this.addBranchList(new BranchList({
                    el: this.$el.find('#date-section')[0],
                    data: this.data,
                    dataKey: 'DATE_OF_PUBLICATION.E50',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));

            }
        });
    }
);