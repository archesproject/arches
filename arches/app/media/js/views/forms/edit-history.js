define(['jquery', 'backbone', 'arches', 'knockout', 'knockout-mapping'], function ($, Backbone, arches, ko, koMapping) {
    return Backbone.View.extend({

        events: function(){
            return {
                'click [name="morehistory"]': 'load'  
            }
        },

        initialize: function() {
            this.el = this.$el.find('#edit-history')[0];
            this.start = 0;
            this.limit = 5;

            this.viewModel = koMapping.fromJS({'history': []});
            ko.applyBindings(this.viewModel, this.el);
            
            this.load(this.start, this.limit);
        },

        load: function(){
            var self = this;
            var count = this.start + this.limit;
            var pathparts = window.location.href.split('/');
            var resourceid = pathparts[pathparts.length-1];
            $.ajax({
                url: arches.urls.edit_history.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', resourceid) + '?start=' + this.start + '&limit=' + count, 
                success: function(response) {
                    if(response.length === 0){
                        $('[name="morehistory"]').addClass('disabled');
                    }
                    $.each(response, function(){
                        var data = koMapping.fromJS(this);
                        self.viewModel.history.push({
                            date: data.date,
                            time: data.time,
                            log: data.log
                        });
                    });
                    self.start = count;
                }
            });
        }
    });
});
