define(['jquery', 'backbone', 'arches', 'models/concept'], function ($, Backbone, arches, ConceptModel) {
    return Backbone.View.extend({

        events: {
            'click .modal-footer .savebtn': 'save',
            'click .modal-footer .btn-u-default': 'cancel',
            'click a': 'removeRelationship'
        },

        initialize: function(){
            var self = this;
            self.$el.find("#error_text").closest('.row').addClass('hidden');
            self.$el.find("[name=concept_identifiers]").val('');
            this.endpoint = this.$el.find('#sparql_endpoint').select2({
                minimumResultsForSearch: -1
            });
            this.$el.find('input.concept_import').select2({
                // multiple: false,
                // maximumselectionsize: 1,
                minimumInputLength: 2,
                id: function(result){ return result.Subject.value; },
                ajax: {
                    url: arches.urls.search_sparql_endpoint,
                    dataType: 'json',
                    data: function (term, page) {
                        return {
                            terms: term,
                            endpoint: self.endpoint.val()
                        };
                    },
                    results: function (data, page) {
                        return {results: data.results.bindings};
                    }
                },
                formatResult:function(result, container, query, escapeMarkup){
                    var markup=[];
                    window.Select2.util.markMatch(result.Term.value, query.term, markup, escapeMarkup);
                    if (!result.ScopeNote){
                        result.ScopeNote = {'value': ''}
                    }
                    var formatedresult = '<span class="concept_result">' + markup.join("")  + '</span> - <a href="' + result.Subject.value + '" target="_blank">' + result.Subject.value + '</a><div><i class="concept_result_schemaname">(' + result.ScopeNote.value + ')</i></div>';
                    return formatedresult;
                },
                escapeMarkup: function(m) { return m; }
            }).on("select2-selecting", function(e, el) {
                self.trigger("select2-selecting", e, el);
                self.$el.find("[name=concept_identifiers]").val(e.val);
            });      

            this.modal = this.$el.find('form');
        },

        save: function(){
            var self = this;
            var data = {
                'ids': this.$el.find("[name=concept_identifiers]").val(),
                'endpoint': this.endpoint.val(),
                'model': this.model.toJSON()
            };
            self.$el.find("#error_text").closest('.row').addClass('hidden');
            $.ajax({
                type: "POST",
                url: arches.urls.from_sparql_endpoint.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.model.get('id')),
                data: JSON.stringify(data),
                success: function(){
                    self.modal.on('hidden.bs.modal', function (e) {
                        self.trigger('conceptsImported');
                    })
                    self.modal.modal('hide');
                }, 
                error: function(response){
                    var el = self.$el.find("#error_text");
                    el.closest('.row').removeClass('hidden');
                    el.html(response.responseText);
                }
            });
            // this.modal.validate({
            //     ignore: null,
            //     rules: {
            //         concept_identifiers: "required"
            //     },
            //     submitHandler: function(form) {
            //         $.ajax({
            //             type: "POST",
            //             url: arches.urls.from_sparql_endpoint.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.model.get('id')),
            //             data: JSON.stringify(data),
            //             success: function(){
            //                 self.modal.on('hidden.bs.modal', function (e) {
            //                     self.trigger('conceptsImported');
            //                 })
            //                 self.modal.modal('hide');
            //             }, 
            //             error: function(response){
            //                 var el = self.$el.find("#error_text");
            //                 el.closest('.row').removeClass('hidden');
            //                 el.html(response.responseText);
            //             }
            //         });
            //     }
            // });
        }
    });
});