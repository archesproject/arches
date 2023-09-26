define(['jquery', 'backbone', 'arches'], function($, Backbone, arches) {
    return Backbone.View.extend({

        initialize: function(options){
            var self = this;
            this.modal = this.$el.find('.modal');
            this.viewModel = options.viewModel;

            this.select2 = this.$el.find('[name=language_dd]').select2({
                minimumResultsForSearch: -1
            });                

            this.modal.validate({
                ignore: null,
                rules: {
                    skosfile: "required",
                    overwrite_options: "required"
                },
                submitHandler: function(form) {
                    var data = new FormData(form);
                    self.viewModel.loading(true);
                    $.ajax({
                        url: arches.urls.concept.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', ''),
                        type: 'POST',
                        data: data,
                        processData: false,
                        contentType: false,
                        complete: function(response, status){
                            self.modal.modal('hide');
                            self.viewModel.loading(false);
                            self.trigger('conceptSchemeAdded', response, status);
                        }
                    });

                    return false;
                }
            });            
        }
    });
});