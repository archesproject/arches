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
                    el: this.$el.find('#assessment-section')[0],
                    data: this.data,
                    dataKey: 'DATE_INTERPRETATION_INFERENCE_MAKING.I5',
                    rules: true,
                    validateBranch: function (nodes) {
                        var canBeEmpty = [
                            'CULTURAL_PERIOD_DETAIL_TYPE.E55',
                            'ARCHAEOLOGICAL_FROM_DATE.E61',
                            'ARCHAEOLOGICAL_TO_DATE.E61',
                            'DATE_INTERPRETATION_INFERENCE_MAKING_ACTOR_NAME.E41'
                        ]
                        var ck0 = this.validateHasValues(nodes, canBeEmpty);
                        var ck1 = vt.isValidDate(nodes,'ARCHAEOLOGICAL_FROM_DATE.E61');
                        var ck2 = vt.isValidDate(nodes,'ARCHAEOLOGICAL_TO_DATE.E61');
                        return ck0 && ck1 && ck2;
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