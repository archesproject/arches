define([
    'jquery',
    'underscore',
    'views/forms/base',
    'views/forms/sections/branch-list',
    'views/forms/sections/location-branch-list',
    'summernote'
], function ($, _, BaseForm, BranchList, LocationBranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);

            this.addBranchList(new LocationBranchList({
                el: this.$el.find('#geom-list-section')[0],
                data: this.data,
                dataKey: 'SPATIAL_COORDINATES_GEOMETRY.E47'
            }));

        }
    });
});