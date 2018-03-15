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
            
            _.each(this.data["ADMINISTRATIVE_DIVISION.E53"].domains["ADMINISTRATIVE_DIVISION_TYPE.E55"], function (typeRecord) {
                adminAreaTypeLookup[typeRecord.text] = typeRecord.id;
            });

            if (includeMap) {
                var locationBranchList = new LocationBranchList({
                    el: this.$el.find('#geom-list-section')[0],
                    data: this.data,
                    dataKey: 'GEOMETRIC_PLACE_EXPRESSION.SP5'
                });
                locationBranchList.on('geometrychange', function(feature, wkt) {
                    $.ajax({
                        url: arches.urls.get_admin_areas + '?geom=' + wkt,
                        success: function (response) {
                            _.each(response.results, function(item) {
                                var duplicate = false;
                                _.each(adminAreaBranchList.viewModel.branch_lists(), function(branch) {
                                    var sameName = false;
                                    var sameType = false;
                                    _.each(branch.nodes(), function (node) {
                                        if (node.entitytypeid() === "ADMINISTRATIVE_DIVISION_TYPE.E55" &&
                                            node.label() === item.overlayty) {
                                            sameType = true;
                                        }
                                        if (node.entitytypeid() === "ADMINISTRATIVE_DIVISION.E53" &&
                                            node.value() === item.overlayval) {
                                            sameName = true;
                                        }
                                    });
                                    if (sameName && sameType) {
                                        duplicate = true;
                                    }
                                });
                                if (adminAreaTypeLookup[item.overlayty] && !duplicate) {
                                    adminAreaBranchList.viewModel.branch_lists.push(koMapping.fromJS({
                                        'editing':ko.observable(false),
                                        'nodes': ko.observableArray([
                                            koMapping.fromJS({
                                              "property": "",
                                              "entitytypeid": "ADMINISTRATIVE_DIVISION_TYPE.E55",
                                              "entityid": "",
                                              "value": adminAreaTypeLookup[item.overlayty],
                                              "label": item.overlayty,
                                              "businesstablename": "",
                                              "child_entities": []
                                            }),
                                            koMapping.fromJS({
                                              "property": "",
                                              "entitytypeid": "ADMINISTRATIVE_DIVISION.E53",
                                              "entityid": "",
                                              "value": item.overlayval,
                                              "label": "",
                                              "businesstablename": "",
                                              "child_entities": []
                                            })
                                        ])
                                    }));
                                }
                            });
                        }
                    })
                });
                this.addBranchList(locationBranchList);
            }
            
            this.addBranchList(new BranchList({
                el: this.$el.find('#certainty-of-geometry')[0],
                data: this.data,
                dataKey: 'GEOMETRY_EXTENT_CERTAINTY.I6',
                rules: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));

            this.addBranchList(new BranchList({
                el: this.$el.find('#grid_ID-section')[0],
                data: this.data,
                dataKey: 'GRID_ID.E42',
                rules: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));
            
            this.addBranchList(new BranchList({
                el: this.$el.find('#siteshape-section')[0],
                data: this.data,
                dataKey: 'SITE_OVERALL_SHAPE_TYPE.E55',
                rules: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));

            this.addBranchList(new BranchList({
                el: this.$el.find('#topography')[0],
                data: this.data,
                dataKey: 'TOPOGRAPHY_TYPE.E55',
                rules: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));

            this.addBranchList(new BranchList({
                el: this.$el.find('#country')[0],
                data: this.data,
                dataKey: 'COUNTRY_TYPE.E55',
                rules: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));

            this.addBranchList(new BranchList({
                el: this.$el.find('#administrative-area')[0],
                data: this.data,
                dataKey: 'ADMINISTRATIVE_DIVISION.E53',
                rules: true,
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
        }
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