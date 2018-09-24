define(['jquery', 
    'underscore', 
    'knockout-mapping', 
    'views/forms/base', 
    'views/forms/sections/branch-list',
    'views/forms/sections/validation',
    'bootstrap-datetimepicker',], 
    function ($, _, koMapping, BaseForm, BranchList, ValidationTools) {
        var vt = new ValidationTools;
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
                        var canBeEmpty = [
                            'DATE_INFERENCE_MAKING_ACTOR_NAME.E41',
                            'CULTURAL_PERIOD_DETAIL_TYPE.E55'
                        ];
                        return this.validateHasValues(nodes,canBeEmpty);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#period-of-occupation')[0],
                    data: this.data,
                    dataKey: 'ARCHAEOLOGICAL_TIMESPAN.E52',
                    validateBranch: function (nodes) {
                        var ck0 = this.validateHasValues(nodes);
                        var ck1 =vt.isValidDate(nodes,'ARCHAEOLOGICAL_FROM_DATE.E61');
                        var ck2 =vt.isValidDate(nodes,'ARCHAEOLOGICAL_TO_DATE.E61');
                        return ck0 && ck1&& ck2;
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
                    rules: false,
                    validateBranch: function (nodes) {
                        var canBeEmpty = [
                        
                            'FEATURE_FORM_TYPE.I4',
                            'FEATURE_FORM_TYPE_CERTAINTY.I6',
                            'FEATURE_SHAPE_TYPE.E55',
                            'FEATURE_ARRANGEMENT_TYPE.E55',
                            'FEATURE_NUMBER_TYPE.E55',
                            'FEATURE_ASSIGNMENT_INVESTIGATOR_NAME.E41'
                        
                        
                        ];
                        return this.validateHasValues(nodes,canBeEmpty);
                    }
                }));
                this.addBranchList(new BranchList({
                    el: this.$el.find('#feature-interpretation')[0],
                    data: this.data,
                    dataKey: 'FUNCTION_INTERPRETATION_INFERENCE_MAKING.I5',
                    rules: true,
                    validateBranch: function (nodes) {
                        var canBeEmpty = ['FUNCTION_INTERPRETATION_INFERENCE_MAKING_ACTOR_NAME.E41'];
                        return this.validateHasValues(nodes,canBeEmpty);
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