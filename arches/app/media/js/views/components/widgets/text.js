define(['knockout', 'underscore', 'viewmodels/widget', 'arches', 'bindings/chosen'], function (ko, _, WidgetViewModel, arches) {
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
            self.currentLanguage = ko.observable({code: arches.defaultLanguage});
            self.languages = ko.observableArray();
            self.currentText = ko.observable();
            self.currentDirection = ko.observable();
            const currentValue = ko.unwrap(self.value) || {};

            const originalValue = JSON.stringify(self.value());

            if(self.form){
                self.form.on('tile-reset', (x) => {
                    self.value(JSON.parse(originalValue));
                    currentValue = self.value();
                });
            }

            const init = async() => {
                const languages = (await $.getJSON(arches.urls.languages))?.languages;
                const currentLanguage = languages?.find(x => x.code == arches.defaultLanguage);
                self.languages(languages);
                self.currentLanguage(currentLanguage);
    
                if(!currentValue?.[currentLanguage.code]){
                    self.currentText('');
                    self.currentDirection('ltr');
                    currentValue[currentLanguage.code] = {value: '', direction: 'ltr'}
                } else {
                    self.currentText(currentValue?.[currentLanguage.code]?.value);
                    self.currentDirection(currentValue?.[currentLanguage.code]?.direction);
                }
            }

            init();

            self.disable = ko.computed(() => {
                return ko.unwrap(self.disabled) || ko.unwrap(self.uneditable); 
            }, self);

            self.currentText.subscribe(x => {
                const currentLanguage = self.currentLanguage();
                if(!currentLanguage) { return; }
                currentValue[currentLanguage.code].value = x;
                self.value(currentValue);
            });

            self.currentDirection.subscribe(x => {
                const currentLanguage = self.currentLanguage();
                if(!currentLanguage) { return; }
                if(!currentValue?.[currentLanguage.code]){
                    currentValue[currentLanguage.code] = {}
                }
                currentValue[currentLanguage.code].direction = x;
                self.value(currentValue);
            })

            self.currentLanguage.subscribe(x => {
                if(!x){ return; }
                const currentValue = self.value() || {};
                const currentLanguage = self.currentLanguage();
                if(!self.value()?.[currentLanguage.code]) {
                    currentValue[currentLanguage.code] = {
                        value: '',
                        direction: currentLanguage?.default_direction
                    }
                    self.value(currentValue);
                }

                self.currentText(self.value()?.[currentLanguage.code]?.value);
                self.currentDirection(self.value()?.[currentLanguage.code]?.direction);
                
            });

        },
        template: { require: 'text!widget-templates/text' }
    });
});
