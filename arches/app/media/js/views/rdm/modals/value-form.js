define(['jquery', 'backbone', 'bootstrap', 'select2'], function ($, Backbone) {
    return Backbone.View.extend({
        modal: null,
        initialize: function(options) {
            var self = this,
                rules = {},
                modal, titles;

            switch(this.model.get('category')) {
                case 'label':
                    modal = this.$el.find('#labelmodal');
                    break;
                case 'note':
                    modal = this.$el.find('#notemodal');
                    break;
                default:
                    modal = this.$el.find('#related_valuemodal');
            }

            titles = modal.find('.modal-title').data();
            modal.find('.modal-title').text(titles[this.model.get('id') ? 'editTitle' : 'addTitle']);
            
            this.valueInput = modal.find('.value-input');
            this.idInput = modal.find('.id-input');
            this.valueTypeInput = modal.find('select.value-type-input');
            this.languageInput = modal.find('select.language-input');
            this.languageInput.select2({
                minimumResultsForSearch: 10,
                maximumSelectionSize: 1
            });
            this.valueTypeInput.select2({
                minimumResultsForSearch: 10,
                maximumSelectionSize: 1
            });
            
            rules[this.valueInput.attr('id')] = "required";
            rules[this.valueTypeInput.attr('id')] = "required";
            rules[this.languageInput.attr('id')] = "required";

            modal.validate({
                ignore: null,
                rules: rules,
                submitHandler: function(form) {
                    self.model.set({
                        value: self.valueInput.val(),
                        id: self.idInput.val(),
                        type: self.valueTypeInput.select2("val")[0],
                        datatype: 'text',
                        language: self.languageInput.select2("val")[0]
                    });
                    self.model.save(function() {
                        modal.on('hidden.bs.modal', function () {
                            self.trigger('save', self.model);
                        });
                        modal.modal('hide');
                    });
                }
            });

            this.model.on('change', function () {
                self.render();
            });

            this.render();
            modal.modal('show');
        },
        
        render: function () {
            this.valueInput.val(this.model.get('value'));
            this.idInput.val(this.model.get('id'));
            this.valueTypeInput.select2("val", this.model.get('type'));
            this.languageInput.select2("val", this.model.get('language'));
        }
    });
});