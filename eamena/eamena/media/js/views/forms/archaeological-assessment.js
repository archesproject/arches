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
                    el: this.$el.find('#overall-archaeological-certainty')[0],
                    data: this.data,
                    dataKey: 'ARCHAEOLOGICAL_CERTAINTY_OBSERVATION.S4',
                    rules: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#date-inference-making')[0],
                    data: this.data,
                    dataKey: 'DATE_INFERENCE_MAKING.I5',
                    rules: true,
                    validateBranch: function (nodes) {
                        var canBeEmpty = ['DATE_INFERENCE_MAKING_ACTOR_NAME.E41'];
                        var valid = nodes != undefined && nodes.length > 0;
                        _.each(nodes, function (node) {
                            if (node.entityid === '' && node.value === '' &&
                                canBeEmpty.indexOf(node.entitytypeid) == -1
                            ){
                                valid = false;
                            }
                        }, this);
                        return valid;
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#period-of-occupation')[0],
                    data: this.data,
                    dataKey: 'ARCHAEOLOGICAL_TIMESPAN.E52',
                    rules: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#overall-morphology')[0],
                    data: this.data,
                    dataKey: 'FEATURE_MORPHOLOGY_TYPE.E55',
                    rules: true,
                    validateBranch: function (nodes) {
                        return this.validateHasValues(nodes);
                    }
                }));
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#feature-morphology')[0],
                    data: this.data,
                    dataKey: 'FEATURE_ASSIGNMENT.E13',
                    rules: true,
                    validateBranch: function (nodes) {
                        var canBeEmpty = ['FEATURE_ASSIGNMENT_INVESTIGATOR_NAME.E41'];
                        var valid = nodes != undefined && nodes.length > 0;
                        _.each(nodes, function (node) {
                            if (node.entityid === '' && node.value === '' &&
                                canBeEmpty.indexOf(node.entitytypeid) == -1
                            ){
                                valid = false;
                            }
                        }, this);
                        return valid;
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#feature-interpretation')[0],
                    data: this.data,
                    dataKey: 'FUNCTION_INTERPRETATION_INFERENCE_MAKING.I5',
                    rules: true,
                    validateBranch: function (nodes) {
                        var canBeEmpty = ['FUNCTION_INTERPRETATION_INFERENCE_MAKING_ACTOR_NAME.E41'];
                        var valid = nodes != undefined && nodes.length > 0;
                        _.each(nodes, function (node) {
                            if (node.entityid === '' && node.value === '' &&
                                canBeEmpty.indexOf(node.entitytypeid) == -1
                            ){
                                valid = false;
                            }
                        }, this);
                        return valid;
                    }
                }));
            },
            
            toggleEditActor: function (e) {
                var actorClass = e.target.dataset.actor;
                if ($(e.target).hasClass("show-box")) {
                    $(".show-box." + actorClass).addClass('hidden');
                    $(".hide-box." + actorClass).removeClass('hidden');
                    $(".edit-actors-row." + actorClass).removeClass('hidden');
                } else {
                    $(".show-box." + actorClass).removeClass('hidden');
                    $(".hide-box." + actorClass).addClass('hidden');
                    $(".edit-actors-row." + actorClass).addClass('hidden');
                }
            },
            
            events: function(){
                var events = BaseForm.prototype.events.apply(this);
                events['click .edit-actor'] = 'toggleEditActor';
                return events;
            },

        });
    }
);