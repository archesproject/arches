define(['jquery', 'backbone', 'arches', 'models/concept', 'models/value'], function($, Backbone, arches, ConceptModel, ValueModel) {
    return Backbone.View.extend({

        initialize: function(options){
            var self = this;
            this.modal = this.$el.find('.modal');
            this.viewModel = options.viewModel;

            // test to see if select2 has already been applied to the dom
            if (! this.$el.find('.select2').attr('id')){
                this.schemedropdown = this.$el.find('.select2').select2({
                    placeholder: arches.translations.selectAnOption
                })
                    .on("select2:selecting", function(e) {
                        $.ajax({
                            url: arches.urls.confirm_delete.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', e.params.args.data.id),
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
                    self.viewModel.loading(true);
                    self.model = new ConceptModel({
                        'id':self.schemedropdown.val(),
                        'nodetype': 'ConceptScheme', 
                        'delete_self': true
                    });

                    self.model.delete(function(){
                        self.modal.modal('hide');
                        self.viewModel.loading(true);
                        self.trigger('conceptSchemeDeleted');
                    }, self);
                }
                
            });            
        }
    });
});