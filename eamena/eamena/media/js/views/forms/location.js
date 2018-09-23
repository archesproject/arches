define([
    'jquery',
    'underscore',
    'arches',
    'knockout', 
    'knockout-mapping', 
    'views/forms/base',
    'views/forms/sections/branch-list',
    'views/forms/sections/location-branch-list',
    'summernote'
], function ($, _, arches, ko, koMapping, BaseForm, BranchList, LocationBranchList) {
    return BaseForm.extend({
        initialize: function() {
            var self = this;
            var resourcetypeid = $('#resourcetypeid').val();
            var includeMap = (resourcetypeid !== 'ACTOR.E39');
            var adminAreaTypeLookup = {};
            BaseForm.prototype.initialize.apply(this);
            var OverlapModel = {
                over: ko.observableArray([])
            }
            ko.applyBindings(OverlapModel,document.getElementById('list_overlaps'));            
            _.each(this.data["ADMINISTRATIVE_DIVISION.E53"].domains["ADMINISTRATIVE_DIVISION_TYPE.E55"], function (typeRecord) {
                adminAreaTypeLookup[typeRecord.text] = typeRecord.id;
            });

            if (includeMap) {
                var locationBranchList = new LocationBranchList({
                    el: this.$el.find('#geom-list-section')[0],
                    data: this.data,
                    dataKey: 'GEOMETRIC_PLACE_EXPRESSION.SP5'
                });
                locationBranchList.on('geometryadded', function(feature, wkt) {
                    $.ajax({
                        url: arches.urls.find_overlapping_data + '?geom=' + wkt,
                        success: function (response) {
                                if (response.length > 0) {
                                    showOverlapsWarning(response);
                                }
                        }
                    })
                });
                this.addBranchList(locationBranchList);
            }
            var showOverlapsWarning = function(overlaps) {
                _.each(overlaps,function(item) {
                    item['id'] = arches.urls.resource_manager+item['id'];
                    OverlapModel.over.push(item);
                });            
                $('#Disclaimer').modal('show');
                
             }
            this.addBranchList(new BranchList({
                el: this.$el.find('#certainty-of-geometry')[0],
                data: this.data,
                dataKey: 'GEOMETRY_EXTENT_CERTAINTY.I6',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));
            
            if (resourcetypeid == 'HERITAGE_FEATURE.E24') {
                var siteshape_node = 'SITE_OVERALL_SHAPE_TYPE.E55';
                var grid_node = 'GRID_ID.E42';
            } else { 
                var siteshape_node = 'SITE_OVERALL_SHAPE_TYPE_NEW.E55';
                var grid_node = 'GRID_ID_NEW.E42';
            }
            
            this.addBranchList(new BranchList({
                el: this.$el.find('#grid_ID-section')[0],
                data: this.data,
                dataKey: grid_node,

                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));
    
            
            this.addBranchList(new BranchList({
                el: this.$el.find('#siteshape-section')[0],
                data: this.data,
                dataKey: siteshape_node,

                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));

            this.addBranchList(new BranchList({
                el: this.$el.find('#topography')[0],
                data: this.data,
                dataKey: 'TOPOGRAPHY_TYPE.E55',

                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));

            this.addBranchList(new BranchList({
                el: this.$el.find('#country')[0],
                data: this.data,
                dataKey: 'COUNTRY_TYPE.E55',

                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));

            this.addBranchList(new BranchList({
                el: this.$el.find('#administrative-area')[0],
                data: this.data,
                dataKey: 'ADMINISTRATIVE_DIVISION.E53',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));
            
            this.addBranchList(new BranchList({
                el: this.$el.find('#address')[0],
                data: this.data,
                dataKey: 'ADDRESS.E45',
            }));
            
            this.addBranchList(new BranchList({
                el: this.$el.find('#cadastral-reference')[0],
                data: this.data,
                dataKey: 'CADASTRAL_REFERENCE.E44',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));
        },    
    });
});


$(function($) {
    PlusMinus = true;	
    $('#plusminus').click(function() {
        var wasPlay = $(this).hasClass('fa-plus-square');
        $(this).removeClass('fa-plus-square fa-minus-square');
        var klass = wasPlay ? 'fa-minus-square' : 'fa-plus-square';
        $(this).addClass(klass)
        if (PlusMinus == true) {
            $('#tobehidden').show();
        } else {
            $('#tobehidden').hide();
        }
        PlusMinus = !PlusMinus;
    }); 
    
});