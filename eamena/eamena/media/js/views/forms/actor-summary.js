define(['jquery', 'underscore', 'knockout-mapping', 'views/forms/base', 'views/forms/sections/branch-list'], function ($, _, koMapping, BaseForm, BranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);


            this.addBranchList(new BranchList({
                el: this.$el.find('#name-section')[0],
                data: this.data,
                dataKey: 'ACTOR_APPELLATION.E82',
                validateBranch: function (nodes) {
                    var valid = true;
                    var primaryname_count = 0;
                    var primaryname_conceptid = this.viewModel.primaryname_conceptid;
                    _.each(nodes, function (node) {
                        if (node.entitytypeid === 'ACTOR_APPELLATION.E82') {
                            if (node.value === ''){
                                valid = false;
                            }
                        }
                    }, this);
                    return valid;
                }
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#organisation-type-section')[0],
                data: this.data,
                dataKey: 'ORGANISATION_TYPE.E55',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            })); 
            this.addBranchList(new BranchList({
                el: this.$el.find('#country-section')[0],
                data: this.data,
                dataKey: 'MODERN_COUNTRY_TERRITORY.E55',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));               
        }
    });
});

