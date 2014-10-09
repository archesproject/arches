define(['jquery', 'backbone', 'bootstrap', 'select2'], function ($, Backbone) {
    return Backbone.View.extend({
        modal: null,
        initialize: function(options) {
            var self = this,
                rules = {},
                title = 'Add New ';
            
            if (this.model.get('id')) {
                title = 'Edit ';
            }
            switch($(this.el).attr('id')) {
                case 'labelmodal':
                    title += 'Label';
                    break;
                case 'notemodal':
                    title += 'Note';
                    break;
                case 'related_valuemodal':
                    title += 'Related Value';
                    break;
                default:
                    title += 'Value';
            }

            $(this.el).find('.modal-title').text(title);
            
            this.valueInput = $(this.el).find('.value-input');
            this.idInput = $(this.el).find('.id-input');
            this.valueTypeInput = $(this.el).find('.value-type-input');
            this.languageInput = $(this.el).find('.language-input');
            
            rules[this.valueInput.attr('id')] = "required";
            rules[this.valueTypeInput.attr('id')] = "required";
            rules[this.languageInput.attr('id')] = "required";

            $(this.el).validate({
                ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
                rules: rules,
                submitHandler: function(form) {
                    self.model.set({
                        value: self.valueInput.val(),
                        id: self.idInput.val(),
                        valuetype: self.valueTypeInput.select2('val'),
                        datatype: 'text',
                        language: self.languageInput.select2('val')
                    });
                    $(this.el).modal('hide');
                    self.trigger('submit');
                }
            });

            this.model.on('change', function () {
                self.render();
            });

            this.render();
            $(this.el).modal('show');
        },
        
        render: function () {
            this.valueInput.val(this.model.get('value'));
            this.idInput.val(this.model.get('id'));
            this.valueTypeInput.select2("val", this.model.get('type'));
            this.languageInput.select2("val", this.model.get('language'));
        }
    });
});