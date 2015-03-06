define(['jquery', 'backbone', 'arches'], function ($, Backbone, arches) {
    return Backbone.View.extend({

        initialize: function(e){
            var self = this;
            this.modal = this.$el.find('.modal');

            this.select2 = this.$el.find('[name=language_dd]').select2({
                minimumResultsForSearch: -1
            });                

            this.modal.validate({
                ignore: null,
                rules: {
                    skosfile: "required"
                },
                submitHandler: function(form) {
                    $(form).submit(function(e) {
                        
                        var data = new FormData(this);

                        $.ajax({
                            url: arches.urls.concept.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', ''),
                            type: 'POST',
                            data: data,
                            processData: false,
                            contentType: false,
                            complete: function(xhr, status){
                                self.modal.modal('hide');
                                $('.modal-backdrop.fade.in').remove();  // a hack for now
                                self.trigger('conceptSchemeAdded');
                                
                                if (status === 'success'){
                                    
                                }else{

                                }
                            }
                        });
                        e.preventDefault();
                    });
                }
            });            
        }
    });
});