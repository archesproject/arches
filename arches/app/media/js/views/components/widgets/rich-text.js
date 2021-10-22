define(['knockout', 'underscore', 'viewmodels/widget', 'arches', 'bindings/ckeditor', 'bindings/chosen'], function (ko, _, WidgetViewModel, arches) {
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
            const initialCurrent = {};
            initialCurrent[arches.defaultLanguage] = {value: '', direction: 'ltr'};
            let currentValue = ko.unwrap(self.value) || initialCurrent;
            const currentLanguage = {"code": arches.defaultLanguage};
            self.currentLanguage = ko.observable(currentLanguage);

            if(self.form){
                const originalValue = JSON.parse(JSON.stringify(self.value()));
                self.form.on('tile-reset', (x) => {
                    self.value(originalValue);
                });
            }

            const languages = arches.languages;
            self.languages =  ko.observableArray(languages);
            self.currentLanguage(languages.find(element => element.code == arches.defaultLanguage));

            if(!currentValue?.[currentLanguage.code]){
                self.currentText = ko.observable('');
                self.currentDirection = ko.observable('ltr');
                currentValue[currentLanguage.code] = {value: '', direction: 'ltr'}
            } else {
                self.currentText = ko.observable(currentValue?.[currentLanguage.code]?.value);
                self.currentDirection = ko.observable(currentValue?.[currentLanguage.code]?.direction);
            }

            self.strippedValue = ko.pureComputed(() => {
                return $(`<span>${self.currentText()}</span>`).text();
            });

            self.strippedValue();
            self.currentText.subscribe(x => {
                const currentLanguage = self.currentLanguage();
                if(!currentLanguage) { return; }
                currentValue[currentLanguage.code].value = x;
                self.value(currentValue);
            });
            self.currentDirection.subscribe(x => {
                const currentLanguage = self.currentLanguage();
                if(!currentLanguage) { return; }
                currentValue[currentLanguage.code].direction = x;
                self.value(currentValue);
            })

            self.currentLanguage.subscribe(() => {
                if(!self.currentLanguage()){ return; }

                const currentLanguage = self.currentLanguage()
                if(!currentValue?.[currentLanguage.code]) {
                    currentValue[currentLanguage.code] = {
                        value: '',
                        direction: currentLanguage?.default_direction
                    }
                    self.value(currentValue);
                }

                self.currentText(self.value()?.[currentLanguage.code]?.value);
                self.currentDirection(self.value()?.[currentLanguage.code]?.direction);
                
            });

            this.displayfullvalue(params.displayfullvalue);
        },
        template: { require: 'text!widget-templates/rich-text' }
    });
});
