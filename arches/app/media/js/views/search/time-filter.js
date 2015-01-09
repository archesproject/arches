define(['jquery', 
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'select2',
    'knockout',
    'plugins/bootstrap-slider/bootstrap-slider.min',
    'views/forms/sections/branch-list',
    'resource-types',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'], 
    function($, _, Backbone, bootstrap, arches, select2, ko, Slider, BranchList, resourceTypes) {

        return Backbone.View.extend({

            initialize: function(options) { 
                var self = this;
                var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
                var slider = new Slider('input.slider', {});
                
                date_picker.on('dp.change', function(evt){
                    $('#date').trigger('change'); 
                });

                slider.on('slideStop', function(evt){
                    // if ther user has the slider at it's min and max, then essentially they don't want to filter by year
                    if(slider.getAttribute('min') === evt.value[0] && slider.getAttribute('max') === evt.value[1]){
                        self.query.filter.year_min_max([]);
                    }else{
                        self.query.filter.year_min_max(evt.value);
                    }
                });                

                this._rawdata = ko.toJSON(JSON.parse($('#formdata').val()));
                this.viewModel = JSON.parse(this._rawdata);

                this.expanded = ko.observable(false);
                this.expanded.subscribe(function(status){
                    self.toggleFilterSection($('#time-filter'), status)
                });

                this.query = {
                    filter:  {
                        domains: this.viewModel.domains,
                        year_min_max: ko.observableArray(),
                        filters: ko.observableArray(),
                        editing:{
                            filters: {}
                        },
                        defaults:{
                            filters: {
                                date: '',
                                date_types__value: '',
                                date_types__label: '',
                                date_operators__value: '',
                                date_operators__label: ''
                            }
                        } 
                    },
                    isEmpty: function(){
                        if (this.filter.year_min_max.length === 0){
                            return true;
                        }
                        return false;
                    },
                    changed: ko.pureComputed(function(){
                        var ret = ko.toJSON(this.query.filter.year_min_max()) +
                            ko.toJSON(this.query.filter.filters());
                        return ret;
                    }, this).extend({ rateLimit: 200 })
                };

                this.query.filter.year_min_max.subscribe(function(newValue){
                    if(newValue.length == 2){
                        slider.setValue(newValue);
                    }
                });

                new BranchList({
                    el: $('#time-filter')[0],
                    viewModel: this.query.filter,
                    key: 'filters',
                    validateBranch: function (data) {
                        if (data.date_types__value !== '' && data.date_operators__value !== '' && data.date !== '') {
                            return true;
                        }
                        return false;
                    }
                })

                ko.applyBindings(this.query.filter, $('#time-filter')[0]);
            },

            toggleFilterSection: function(ele, expand){
                if(expand){
                    this.slideToggle(ele, 'show');
                }else{
                    this.slideToggle(ele, 'hide');               
                }
            },

            slideToggle: function(ele, showOrHide){
                var self = this;
                if ($(ele).is(":visible") && showOrHide === 'hide'){
                    ele.slideToggle('slow');
                    return;
                }

                if (!($(ele).is(":visible")) && showOrHide === 'show'){
                    ele.slideToggle('slow');
                    return;
                }

                if (!showOrHide){
                    ele.slideToggle('slow');                    
                }
            }

        });

});