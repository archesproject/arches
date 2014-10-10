define(['jquery', 'backbone', 'bootstrap', 'select2'], function ($, Backbone) {
    return Backbone.View.extend({
        modal: null,
        initialize: function(options) {
            var self = this,
                rules = {},
                title;

            switch(this.model.get('category')) {
                case 'label':
                    this.modal = this.$el.find('#labelmodal');
                    break;
                case 'note':
                    this.modal = this.$el.find('#notemodal');
                    break;
                default:
                    this.modal = this.$el.find('#related_valuemodal');
            }
            title = this.modal.find('.modal-title').data()['addTitle'];
            if (this.model.get('id')) {
                title = this.modal.find('.modal-title').data()['editTitle'];
            }

            this.modal.find('.modal-title').text(title);
            
            this.valueInput = this.modal.find('.value-input');
            this.idInput = this.modal.find('.id-input');
            this.valueTypeInput = this.modal.find('.value-type-input');
            this.languageInput = this.modal.find('.language-input');
            
            rules[this.valueInput.attr('id')] = "required";
            rules[this.valueTypeInput.attr('id')] = "required";
            rules[this.languageInput.attr('id')] = "required";

            this.modal.validate({
                ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
                rules: rules,
                submitHandler: function(form) {
                    self.modal.modal('hide');
                    self.model.set({
                        value: self.valueInput.val(),
                        id: self.idInput.val(),
                        valuetype: self.valueTypeInput.val(),
                        datatype: 'text',
                        language: self.languageInput.val()
                    });
                    self.trigger('submit');
                }
            });

            this.model.on('change', function () {
                self.render();
            });

            this.render();
            this.modal.modal('show');
        },
        
        render: function () {
            this.valueInput.val(this.model.get('value'));
            this.idInput.val(this.model.get('id'));
            this.valueTypeInput.select2("val", this.model.get('type'));
            this.languageInput.select2("val", this.model.get('language'));
        }
    });
});