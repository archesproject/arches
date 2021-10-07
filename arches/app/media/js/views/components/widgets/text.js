define(['knockout', 'underscore', 'viewmodels/widget', 'arches'], function (ko, _, WidgetViewModel, arches) {
    /**
    * registers a text-widget component for use in forms
    * @function external:"ko.components".text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    * @param {string} params.config().uneditable - disables widget
    */

    return ko.components.register('text-widget', {
        viewModel: function (params) {
            params.configKeys = ['placeholder', 'width', 'maxLength', 'defaultValue', 'uneditable'];
    
            WidgetViewModel.apply(this, [params]);
    
            const self = this;
    
            self.disable = ko.computed(() => {
                return ko.unwrap(self.disabled) || ko.unwrap(self.uneditable); 
            }, self);

            const currentValue = ko.unwrap(self.value) || {};

            const currentLanguage = arches.defaultLanguage;
            self.currentLanguage = ko.observable(currentLanguage);
            if(!currentValue?.[currentLanguage]){
                self.currentText = ko.observable('');
                self.currentDirection = ko.observable('ltr');
                currentValue[currentLanguage] = {value: '', direction: 'ltr'}
            } else {
                self.currentText = ko.observable(currentValue?.[currentLanguage]?.value);
                self.currentDirection = ko.observable(currentValue?.[currentLanguage]?.direction);
            }
            self.languages = arches.languages;

            self.currentText.subscribe(x => {
                const currentLanguage = self.currentLanguage()
                currentValue[self.currentLanguage()].value = x;
                self.value(currentValue);
            })
            self.currentDirection.subscribe(x => {
                if(!currentValue?.[currentLanguage]){
                    currentValue[currentLanguage] = {}
                }
                currentValue[self.currentLanguage()].direction = x;
                self.value(currentValue);
            })

            self.currentLanguage.subscribe(x => {
                const currentValue = self.value()
                const currentLanguage = x;
                if(!self.value()?.[currentLanguage]) {
                    currentValue[currentLanguage] = {
                        value: '',
                        direction: 'ltr'
                    }
                    self.value(currentValue);
                }

                self.currentText(self.value()?.[currentLanguage]?.value);
                self.currentDirection(self.value()?.[currentLanguage]?.direction);
                
            });

        },
        template: { require: 'text!widget-templates/text' }
    });
});
