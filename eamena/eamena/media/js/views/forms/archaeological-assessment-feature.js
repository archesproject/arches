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
                    el: this.$el.find('#cultural-period-section')[0],
                    data: this.data,
                    dataKey: 'CULTURAL_PERIOD_BELIEF.I2',
                    rules: true,
                    validateBranch: function (nodes) {
                        return true;
                    }
                }));
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#function-interpretation-section')[0],
                    data: this.data,
                    dataKey: 'DATE_INTERPRETATION_INFERENCE_MAKING.I5',
                    rules: true,
                    validateBranch: function (nodes) {
                        return true;
                    }
                }));
                
                this.addBranchList(new BranchList({
                    el: this.$el.find('#timespan-section')[0],
                    data: this.data,
                    dataKey: 'ARCHAEOLOGICAL_TIMESPAN.E52',
                    rules: true,
                    validateBranch: function (nodes) {
                        return true;
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