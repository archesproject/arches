define(['jquery', 'backbone', 'arches'], function ($, Backbone, arches) {
    return Backbone.View.extend({

        initialize: function(e){
            var self = this;
            this.modal = this.$el.find('.modal');
            this.title = this.modal.find('h4').text();

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
                    self.modal.find('h4').text(' ' + self.title);
                    self.modal.find('.modal-title').addClass('loading');
                    $.ajax({
                        url: arches.urls.concept.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', ''),
                        type: 'POST',
                        data: data,
                        processData: false,
                        contentType: false,
                        complete: function(xhr, status){
                            self.modal.find('h4').text(self.title);
                            self.modal.find('.modal-title').removeClass('loading');
                            self.modal.on('hidden.bs.modal', function (e) {
                                self.trigger('conceptSchemeAdded');
                            })
                            self.modal.modal('hide');
                        }
                    });

                    return false;
                }
            });            
        }
    });
});