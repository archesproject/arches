 define(['jquery', 'underscore', 'knockout-mapping', 'views/forms/base', 'views/forms/sections/branch-list'], function ($, _, koMapping, BaseForm, BranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);
                           
            var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
            date_picker.on('dp.change', function(evt){
                $(this).find('input').trigger('change');
            });
                           
            this.addBranchList(new BranchList({
                el: this.$el.find('#threat-state-section')[0],
                data: this.data,
                dataKey: 'THREAT_STATE.E3',
                rules: true,
                validateBranch: function (nodes) {
                    valid = true;
                    _.each(nodes, function (node) {
                      if (node.entitytypeid === 'THREAT_CAUSE_TYPE.E55') {
                          if (node.value === ''){
                              valid = false;
                          }
                      }
                      if (node.entitytypeid === 'THREAT_CAUSE_CERTAINTY_TYPE.E55') {
                          if (node.value === ''){
                              valid = false;
                          }
                      }                      
                    }, this);
                    return valid;
                }
            }));
            
            var maxBranchLists = 6;
            this.data['DISTURBANCE_STATE.E3'].branch_lists.forEach(function (branchList) {
                for (var i = branchList.nodes[0].length; i < maxBranchLists; i++) {
                    branchList.nodes[0].push([
                        {
                            entitytypeid:"DISTURBANCE_EFFECT_1_CERTAINTY_TYPE.E55",
                            value: "", label: "", entityid: "",
                        }, {
                            entitytypeid: "DISTURBANCE_EFFECT_1_TYPE.E55",
                            value: "", label: "", entityid: "",
                        },
                    ])
                }
            })

            this.addBranchList(new BranchList({
                el: this.$el.find('#disturbance-state-section')[0],
                data: this.data,
                dataKey: 'DISTURBANCE_STATE.E3',
                rules: true,
                validateBranch: function (nodes) {
                    var valid = true;
                    _.each(nodes, function (node) {
                      if (node.entitytypeid === 'DISTURBANCE_CAUSE_TYPE.E55') {
                          if (node.value === ''){
                              valid = false;
                          }
                      }
                      if (node.entitytypeid === 'DISTURBANCE_CAUSE_CERTAINTY_TYPE.E55') {
                          if (node.value === ''){
                              valid = false;
                          }
                      }
                      if (node.entitytypeid === 'DISTURBANCE_DATE_TYPE.E55') {
                          if (node.value === ''){
                              valid = false;
                          }
                      } 
                      if (node.entitytypeid === 'DISTURBANCE_DATE_END.E49') {
                          if (node.value === ''){
                              valid = false;
                          }
                      }                                                  
                    }, this);
                    return valid;
                }
            }));
                           
                           
            this.addBranchList(new BranchList({
                el: this.$el.find('#condition-type-section')[0],
                data: this.data,
                dataKey: 'CONDITION_TYPE.E55',
                rules: true,
                validateBranch: function (nodes) {                  
                    return this.validateHasValues(nodes);
                }
            }));
            
            this.addBranchList(new BranchList({
                el: this.$el.find('#disturbance-extent-section')[0],
                data: this.data,
                dataKey: 'DISTURBANCE_EXTENT_TYPE.E55',
                rules: true,
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                }
            }));
        }
    });
});

