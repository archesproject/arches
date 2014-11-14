define(['jquery', 'backbone', 'arches', 'models/concept', 'models/value'], function ($, Backbone, arches, ConceptModel, ValueModel) {
    return Backbone.View.extend({

        initialize: function(e){
            var self = this;
            this.modal = this.$el.find('.modal');

            // test to see if select2 has already been applied to the dom
            if (! this.$el.find('.select2').attr('id')){
                this.schemedropdown = this.$el.find('.select2').select2()
                .on("select2-selecting", function(e, el) {
                    $.ajax({
                        url: arches.urls.confirm_delete.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', e.val),
                        success: function(response) {
                            self.modal.find('.modal-body [name="additional-info"]').html(response);
                        }
                    });     
                });              
            }

            //this.schemedropdown.on('changed')

            this.modal.validate({
                ignore: null,
                rules: {
                    scheme_dd: "required"
                },
                submitHandler: function(form) {
                    model = new ConceptModel({'id':self.schemedropdown.val()})
                    self.model.set('subconcepts', [model]);

                    self.model.delete(function(){
                        self.modal.modal('hide');
                        self.trigger('conceptSchemeDeleted');
                    }, self);
                }
                
            });            
        }
    });
});