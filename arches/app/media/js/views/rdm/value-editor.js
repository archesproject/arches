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
            this.valueTypeInput = modal.find('.value-type-input');
            this.languageInput = modal.find('.language-input');
            
            rules[this.valueInput.attr('id')] = "required";
            rules[this.valueTypeInput.attr('id')] = "required";
            rules[this.languageInput.attr('id')] = "required";

            modal.validate({
                ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
                rules: rules,
                submitHandler: function(form) {
                    self.$el.find('.modal.in').modal('hide');
                    self.model.set({
                        value: self.valueInput.val(),
                        id: self.idInput.val(),
                        valuetype: self.valueTypeInput.val(),
                        datatype: 'text',
                        language: self.languageInput.val()
                    });
                    self.model.save(function() {
                        self.trigger('save', self.model);
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