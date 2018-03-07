define(['jquery', 
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'select2',
    'knockout',
    'knockout-mapping', 
    'plugins/bootstrap-slider/bootstrap-slider.min',
    'views/forms/sections/branch-list',
    'resource-types',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'], 
    function($, _, Backbone, bootstrap, arches, select2, ko, koMapping, Slider, BranchList, resourceTypes) {

        return Backbone.View.extend({

            initialize: function(options) { 
                this.index = options.index;
                var self = this;
                var timeFilterClass = ".arches-time-filter";
                if ( typeof self.index !== 'undefined') {

                    timeFilterClass = '.resource_time_filter_widget'+self.index
                }
                var date_picker = $(timeFilterClass+' .datetimepicker').datetimepicker({pickTime: false});
                
                date_picker.on('dp.change', function(evt){
                    $(timeFilterClass+' #date').trigger('change'); 
                });

                ko.observableArray.fn.get = function(entitytypeid, key) {
                    var allItems = this();
                    var ret = '';
                    _.each(allItems, function(node){
                        if (entitytypeid.search(node.entitytypeid()) > -1){
                            ret = node[key]();
                        }
                    }, this);
                    return ret
                }

                this.slider = new Slider(timeFilterClass+' input.slider', {});
                this.slider.on('slideStop', function(evt){
                    // if ther user has the slider at it's min and max, then essentially they don't want to filter by year
                    if(self.slider.getAttribute('min') === evt.value[0] && self.slider.getAttribute('max') === evt.value[1]){
                        self.query.filter.year_min_max.removeAll();
                    }else{
                        self.query.filter.year_min_max(evt.value);
                    }
                    self.trigger('change');
                });                

                this._rawdata = ko.toJSON(JSON.parse($(timeFilterClass+' #timefilterdata').val()));
                this.viewModel = JSON.parse(this._rawdata);

                this.expanded = ko.observable(false);
                this.expanded.subscribe(function(status){
                    // self.toggleFilterSection($('#time-filter'), status)
                    self.toggleFilterSection($(timeFilterClass+'#time-filter'), status)
                });

                this.query = {
                    filter:  {
                        domains: this.viewModel.domains,
                        year_min_max: ko.observableArray(),
                        filters: ko.observableArray(),
                        inverted: ko.observable(false),
                        editing:{
                            filters: {}
                        },
                        defaults:{
                            filters: {
                                date: '',
//                                 date_types__value: '',
//                                 date_types__label: '',
                                date_operators__value: '',
                                date_operators__label: ''
                            }
                        } 
                    },
                    changed: ko.pureComputed(function(){
                        var ret = ko.toJSON(this.query.filter.year_min_max()) +
                            ko.toJSON(this.query.filter.filters()) + 
                            ko.toJSON(this.query.filter.inverted());
                        return ret;
                    }, this).extend({ rateLimit: 200 })
                };

                this.query.filter.year_min_max.subscribe(function(newValue){
                    var sliderenabled = newValue.length === 2;
                    var filtersenabled = this.query.filter.filters().length > 0;
                    if(sliderenabled){
                        self.slider.setValue(newValue);
                    }
                    this.trigger('enabled', filtersenabled || sliderenabled, this.query.filter.inverted());
                }, this);

                this.query.filter.filters.subscribe(function(filters){
                    var filtersenabled = filters.length > 0;
                    var sliderenabled = this.query.filter.year_min_max().length === 2;
                    this.trigger('enabled', filtersenabled || sliderenabled, this.query.filter.inverted());
                }, this);

                this.time_filter_branchlist = new BranchList({
                    // el: $('#time-filter')[0],
                    el: $.find(timeFilterClass+'#time-filter')[0],
                    data: this.viewModel,
                    dataKey: 'date_operators',
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                });

                this.time_filter_branchlist.on('change', function(){
                    self.trigger('change');
                    self.query.filter.filters.removeAll();
                    _.each(this.getData(), function(item){
                        self.query.filter.filters.push(item);
                    })                
                });

                //ko.applyBindings(this.query.filter, $('#time-filter')[0]);
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
            },

            restoreState: function(filter, expanded){
                if(typeof filter !== 'undefined'){
                    if('inverted' in filter){
                        this.query.filter.inverted(filter.inverted);
                    }
                    if('filters' in filter && filter.filters.length > 0){
                        _.each(filter.filters, function(filter){
                            this.query.filter.filters.push(filter);
                            var branch = koMapping.fromJS({
                                'editing':ko.observable(false), 
                                'nodes': ko.observableArray(filter.nodes)
                            });
                            this.time_filter_branchlist.viewModel.branch_lists.push(branch);
                        }, this);
                    }
                    if('year_min_max' in filter && filter.year_min_max.length === 2){
                        _.each(filter.year_min_max, function(year){
                            this.query.filter.year_min_max.push(year);
                        }, this);
                    }
                }

                if(typeof expanded === 'undefined'){
                    expanded = false;
                }
                this.expanded(expanded);

            },

            clear: function(){
                this.query.filter.inverted(false);
                this.query.filter.filters.removeAll();
                this.query.filter.year_min_max.removeAll();
                this.slider.setValue([this.slider.getAttribute('min'),this.slider.getAttribute('max')]);
            }

        });

});