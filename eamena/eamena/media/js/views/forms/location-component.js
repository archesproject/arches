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

            var adminAreaTypeLookup = {};
            BaseForm.prototype.initialize.apply(this);
            var OverlapModel = {
                over: ko.observableArray([])
            }
            ko.applyBindings(OverlapModel,document.getElementById('list_overlaps'));            

            var locationBranchList = new LocationBranchList({
                el: this.$el.find('#geom-list-section')[0],
                data: this.data,
                dataKey: 'SPATIAL_COORDINATES.E47'
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
    });
});