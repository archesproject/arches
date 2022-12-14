define([
    'knockout',
    'knockout-mapping',
    'underscore',
    'viewmodels/widget',
    'arches',
    'templates/views/components/widgets/text.htm',
    'bindings/chosen'
], function(ko, koMapping, _, WidgetViewModel, arches, textWidgetTemplate) {
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

    const viewModel = function(params) {
        params.configKeys = ['placeholder', 'width', 'maxLength', 'defaultValue', 'uneditable'];

        WidgetViewModel.apply(this, [params]);
        const self = this;

        self.card = params.card;
        self.currentLanguage = ko.observable({code: arches.activeLanguage});
        self.languages = ko.observableArray();
        self.currentText = ko.observable();
        self.currentDirection = ko.observable();
        self.showi18nOptions = ko.observable(false);

        self.currentDefaultText = ko.observable();
        self.currentDefaultDirection = ko.observable();
        self.currentDefaultLanguage = ko.observable({code: arches.activeLanguage});

        const initialCurrent = {};
        const initialDefault = {};
        initialDefault[arches.activeLanguage] = {value: '', direction: 'ltr'};
        initialCurrent[arches.activeLanguage] = {value: '', direction: 'ltr'};
        let currentDefaultValue = ko.unwrap(self.defaultValue) || initialDefault;
        let currentValue = koMapping.toJS(self.value) || initialCurrent;

        if(self.form){
            self.form.on('tile-reset', (x) => {
                currentValue = koMapping.toJS(self.value);
                self.currentText(currentValue[self.currentLanguage().code]?.value);
                self.currentDirection(currentValue[self.currentLanguage().code]?.direction);
            });
        }

        const init = async() => {
            const languages = arches.languages;
            const currentLanguage = languages?.find(element => element.code == arches.activeLanguage);
            self.languages(languages);
            self.currentLanguage(currentLanguage);
            self.currentDefaultLanguage(currentLanguage);

            if (currentLanguage?.code && currentValue?.[currentLanguage.code]){
                self.currentText(currentValue?.[currentLanguage.code]?.value);
                self.currentDirection(currentValue?.[currentLanguage.code]?.direction);
            } else if (!currentLanguage?.code) {
                self.currentText('');
                self.currentDirection('ltr');
            } else if (currentValue) {
                self.currentText('');
                self.currentDirection('ltr');
                currentValue[currentLanguage.code] = {value: '', direction: 'ltr'};
            }

            if(currentLanguage?.code && currentDefaultValue?.[currentLanguage.code]){
                self.currentDefaultText(currentDefaultValue?.[currentLanguage.code]?.value);
                self.currentDefaultDirection(currentDefaultValue?.[currentLanguage.code]?.direction);
            } else if (!currentLanguage?.code) {
                self.currentDefaultText('');
                self.currentDefaultDirection('ltr');
            } else if (currentDefaultValue) {
                self.currentDefaultText('');
                self.currentDefaultDirection('ltr');
                currentDefaultValue[currentLanguage.code] = {value: '', direction: 'ltr'};
            }
        };

        init();

        self.disable = ko.computed(() => {
            return ko.unwrap(self.disabled) || ko.unwrap(self.uneditable);
        }, self);

        self.currentDefaultText.subscribe(newValue => {
            const currentLanguage = self.currentDefaultLanguage();
            if(!currentLanguage) { return; }
            currentDefaultValue[currentLanguage.code].value = newValue;
            self.defaultValue(currentDefaultValue);
            self.card._card.valueHasMutated();
        });

        self.currentDefaultDirection.subscribe(newValue => {
            const currentLanguage = self.currentDefaultLanguage();
            if(!currentLanguage) { return; }
            if(!currentDefaultValue?.[currentLanguage.code]){
                currentDefaultValue[currentLanguage.code] = {};
            }
            currentDefaultValue[currentLanguage.code].direction = newValue;
            self.defaultValue(currentDefaultValue);
            self.card._card.valueHasMutated();
        });

        self.currentDefaultLanguage.subscribe(newValue => {
            if(!self.currentDefaultLanguage()){ return; }
            const currentLanguage = self.currentDefaultLanguage();
            if(!currentDefaultValue?.[currentLanguage.code]) {
                currentDefaultValue[currentLanguage.code] = {
                    value: '',
                    direction: currentLanguage?.default_direction
                };
                self.defaultValue(currentDefaultValue);
                self.card._card.valueHasMutated();
            }

            self.currentDefaultText(self.defaultValue()?.[currentLanguage.code]?.value);
            self.currentDefaultDirection(self.defaultValue()?.[currentLanguage.code]?.direction);

        });

        self.currentText.subscribe(newValue => {
            const currentLanguage = self.currentLanguage();
            if(!currentLanguage) { return; }
            currentValue[currentLanguage.code].value = newValue;
            if (ko.isObservable(self.value)) {
                self.value(currentValue);
            } else {
                self.value[currentLanguage.code].value(newValue);
            }
        });

        self.currentDirection.subscribe(newValue => {
            const currentLanguage = self.currentLanguage();
            if(!currentLanguage) { return; }

            if(!currentValue?.[currentLanguage.code]){
                currentValue[currentLanguage.code] = {};
            }
            currentValue[currentLanguage.code].direction = newValue;
            if (ko.isObservable(self.value)) {
                self.value(currentValue);
            } else {
                self.value[currentLanguage.code].direction(newValue);
            }
        });

        self.currentLanguage.subscribe(() => {
            if(!self.currentLanguage()){ return; }
            const currentLanguage = self.currentLanguage();

            self.currentText(koMapping.toJS(self.value)[currentLanguage.code]?.value);
            self.currentDirection(koMapping.toJS(self.value)[currentLanguage.code]?.direction);

        });

    };

    return ko.components.register('text-widget', {
        viewModel: viewModel,
        template: textWidgetTemplate,
    });
});
