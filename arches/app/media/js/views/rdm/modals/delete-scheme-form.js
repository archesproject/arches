define(['jquery', 'backbone', 'arches', 'models/concept', 'models/value'], function ($, Backbone, arches, ConceptModel, ValueModel) {
    return Backbone.View.extend({

        initialize: function(e){

            if (! this.rendered){
                this.render();
            }

        },

        render: function(){
            var self = this;
            this.rendered = true;
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

            this.schemedropdown.on('changed')

            this.modal.validate({
                ignore: null,
                rules: {
                    scheme_dd: "required"
                },
                submitHandler: function(form) {
                    // var model = new ConceptModel({
                    //     id: '00000000-0000-0000-0000-000000000003'
                    // })
                    // var label = new ValueModel({
                    //     value: $(form).find("[name=label]").val(),
                    //     language: $(form).find("[name=language_dd]").val(),
                    //     category: 'label',
                    //     datatype: 'text',
                    //     type: 'prefLabel'
                    // });
                    // var subconcept = new ConceptModel({
                    //     values: [label],
                    //     relationshiptype: 'has collection'
                    // });
                    // model.set('subconcepts', [subconcept]);
                    // model.save(function() {
                    //     var modal = self.$el.find('#add-scheme-form');
                    //     this.modal.modal('hide');
                    //     $('.modal-backdrop.fade.in').remove();  // a hack for now
                    //     self.trigger('conceptSchemeAdded');
                    // }, self);
                }
            });            
        }
    });
});