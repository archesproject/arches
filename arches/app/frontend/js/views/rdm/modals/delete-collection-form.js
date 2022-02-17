define(['jquery', 'backbone', 'arches', 'models/concept', 'models/value'], function ($, Backbone, arches, ConceptModel, ValueModel) {
    return Backbone.View.extend({

        initialize: function(e){
            var self = this;
            this.modal = this.$el.find('.modal');
            this.title = this.modal.find('h4').text();

            // test to see if select2 has already been applied to the dom
            if (! this.$el.find('.select2').attr('id')){
                this.collectiondropdown = this.$el.find('.select2').select2()
                .on("select2-selecting", function(e, el) {
                    $.ajax({
                        url: arches.urls.confirm_delete.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', e.val),
                        success: function(response) {
                            self.modal.find('.modal-body [name="additional-info"]').html(response);
                        }
                    });     
                });              
            }

            this.modal.validate({
                ignore: null,
                rules: {
                    scheme_dd: "required"
                },
                submitHandler: function(form) {
                    self.modal.find('h4').text(' ' + self.title);
                    self.modal.find('.modal-title').addClass('loading');
                    self.model = new ConceptModel({
                        'id':self.collectiondropdown.val(),
                        'nodetype': 'Collection', 
                        'delete_self': true
                    });

                    self.model.delete(function(){
                        self.modal.find('h4').text(self.title);
                        self.modal.find('.modal-title').removeClass('loading');
                        self.modal.modal('hide');
                        self.trigger('collectionDeleted');
                    }, self);
                }
                
            });            
        }
    });
});