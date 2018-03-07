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
                    el: this.$el.find('#tile-square-details-section')[0],
                    data: this.data,
                    dataKey: 'TILE_SQUARE_DETAILS.E44',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                               
                     
                this.addBranchList(new BranchList({
                    el: this.$el.find('#creation-date-section')[0],
                    data: this.data,
                    dataKey: 'DATE_OF_CREATION.E50',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#map-place-section')[0],
                    data: this.data,
                    dataKey: 'MAP_PLACE_APPELLATION.E44',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
        
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#tile-square-appellation-section')[0],
                    data: this.data,
                    dataKey: 'TILE_SQUARE_APPELLATION.E44',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
        
         
                this.addBranchList(new BranchList({
                    el: this.$el.find('#scale-section')[0],
                    data: this.data,
                    dataKey: 'SCALE_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#projection-section')[0],
                    data: this.data,
                    dataKey: 'PROJECTION_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#series-section')[0],
                    data: this.data,
                    dataKey: 'SERIES_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#creator-section')[0],
                    data: this.data,
                    dataKey: 'CONTRIBUTOR_APPELLATION.E82',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#edition-section')[0],
                    data: this.data,
                    dataKey: 'EDITION.E62',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                               
                this.addBranchList(new BranchList({
                    el: this.$el.find('#map-source-type-section')[0],
                    data: this.data,
                    dataKey: 'MAP_SOURCE_TYPE.E55',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                
            }
        });
    }
);