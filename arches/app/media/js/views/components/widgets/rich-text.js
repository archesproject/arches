define(['knockout', 'underscore', 'viewmodels/widget', 'arches', 'bindings/ckeditor'], function (ko, _, WidgetViewModel, arches) {
    /**
    * registers a rich-text-widget component for use in forms
    * @function external:"ko.components".rich-text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    */
    return ko.components.register('rich-text-widget', {
        viewModel: function(params) {
            params.configKeys = ['displayfullvalue'];
            const self = this;
            WidgetViewModel.apply(self, [params]);
            const currentValue = ko.unwrap(self.value) || {};
            const currentLanguage = arches.defaultLanguage;
            if(!currentValue?.[currentLanguage]){
                self.currentText = ko.observable('');
                self.currentDirection = ko.observable('ltr');
                currentValue[currentLanguage] = {value: '', direction: 'ltr'}
            } else {
                self.currentText = ko.observable(currentValue?.[currentLanguage]?.value);
                self.currentDirection = ko.observable(currentValue?.[currentLanguage]?.direction);
            }
            self.currentLanguage = ko.observable(currentLanguage);
            self.strippedValue = ko.pureComputed(() => {
                return $(`<span>${self.currentText()}</span>`).text();
            });

            self.currentText.subscribe(x => {
                currentValue[self.currentLanguage()].value = x;
                self.value(currentValue);
            })
            self.currentDirection.subscribe(x => {
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

            this.languages = arches.languages;
            this.displayfullvalue(params.displayfullvalue);
        },
        template: { require: 'text!widget-templates/rich-text' }
    });
});
