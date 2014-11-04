define(['jquery', 'backbone', 'bootstrap', 'select2'], function ($, Backbone) {
    return Backbone.View.extend({
        initialize: function(options) {
            var self = this,
                rules = {},
                modal, titles;

            this.valuemodel = this.model.get('values')[0];

            switch(this.valuemodel.get('category')) {
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
            modal.find('.modal-title').text(titles[this.valuemodel.get('id') ? 'editTitle' : 'addTitle']);
            
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
                    self.valuemodel.set({
                        value: self.valueInput.val(),
                        id: self.idInput.val(),
                        type: self.valueTypeInput.select2("val"),
                        datatype: 'text',
                        language: self.languageInput.select2("val")
                    });
                    self.model.set('values', [self.valuemodel]);
                    modal.on('hidden.bs.modal', function () {
                        self.model.save(function() {
                            self.model.set('values', []);
                        });    
                    });

                    modal.modal('hide');
                }
            });

            this.render();
            modal.modal('show');
        },
        
        render: function () {
            this.valueInput.val(this.valuemodel.get('value'));
            this.idInput.val(this.valuemodel.get('id'));
            if(this.valuemodel.get('type') !== ''){
                this.valueTypeInput.select2("val", this.valuemodel.get('type'));
            }
            if(this.valuemodel.get('language') !== ''){
                this.languageInput.select2("val", this.valuemodel.get('language'));                
            }
        }
    });
});