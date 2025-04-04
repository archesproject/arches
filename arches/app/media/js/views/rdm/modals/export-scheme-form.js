import $ from 'jquery';
import Backbone from 'backbone';
import arches from 'arches';
import ValueModel from 'models/value';


export default Backbone.View.extend({

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
            this.schemedropdown = this.$el.find('.select2').select2({
                placeholder: arches.translations.selectAnOption
            });                
        }

        this.modal.validate({
            ignore: null,
            rules: {
                scheme_dd: "required"
            },
            submitHandler: function(form) {
                var scheme = $(form).find("[name=scheme_dd]").val();
                window.open(arches.urls.export_concept.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', scheme),'_blank');
                self.modal.modal('hide');
            }
        });            
    }
});
