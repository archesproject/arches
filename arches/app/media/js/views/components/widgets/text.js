import ko from 'knockout';
import koMapping from 'knockout-mapping';
import _ from 'underscore';
import WidgetViewModel from 'viewmodels/widget';
import arches from 'arches';
import textWidgetTemplate from 'templates/views/components/widgets/text.htm';
import 'bindings/select2-query';


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
    params.configKeys = ['placeholder', 'width', 'maxLength', 'defaultValue'];

    WidgetViewModel.apply(this, [params]);
    const self = this;

    self.card = params.card;
    self.currentLanguage = ko.observable(arches.activeLanguage);
    self.languages = ko.observableArray();
    self.currentText = ko.observable();
    self.currentDirection = ko.observable();
    self.showi18nOptions = ko.observable(false);

    self.currentDefaultText = ko.observable();
    self.currentDefaultDirection = ko.observable();
    self.currentDefaultLanguage = ko.observable(arches.activeLanguage);
    self.currentPlaceholder = ko.observable();

    const initialCurrent = {};
    const initialDefault = {};
    initialDefault[arches.activeLanguage] = {value: '', direction: 'ltr'};
    initialCurrent[arches.activeLanguage] = {value: '', direction: 'ltr'};
    let currentDefaultValue = ko.unwrap(self.defaultValue) || initialDefault;
    let currentValue = koMapping.toJS(self.value) || initialCurrent;

    if(self.form){
        self.form.on('tile-reset', (x) => {
            if (ko.unwrap(self.value)) {
                currentValue = koMapping.toJS(self.value);
                self.currentText(currentValue[self.currentLanguage()]?.value);
                self.currentDirection(currentValue[self.currentLanguage()]?.direction);
            }
        });
    }

    const init = async() => {
        const languages = arches.languages;
        const currentLanguage = languages?.find(element => element.code == arches.activeLanguage)?.code;
        self.languages(languages);
        self.currentLanguage(currentLanguage);
        self.currentDefaultLanguage(currentLanguage);

        if (currentLanguage && currentValue?.[currentLanguage]){
            self.currentText(currentValue?.[currentLanguage]?.value);
            self.currentDirection(currentValue?.[currentLanguage]?.direction);
        } else if (!currentLanguage) {
            self.currentText('');
            self.currentDirection('ltr');
        } else if (currentValue) {
            self.currentText('');
            self.currentDirection('ltr');
            currentValue[currentLanguage] = {value: '', direction: 'ltr'};
        }

        if(currentLanguage && currentDefaultValue?.[currentLanguage]){
            self.currentDefaultText(currentDefaultValue?.[currentLanguage]?.value);
            self.currentDefaultDirection(currentDefaultValue?.[currentLanguage]?.direction);
        } else if (!currentLanguage) {
            self.currentDefaultText('');
            self.currentDefaultDirection('ltr');
        } else if (currentDefaultValue) {
            self.currentDefaultText('');
            self.currentDefaultDirection('ltr');
            currentDefaultValue[currentLanguage] = {value: '', direction: 'ltr'};
        }

        if (ko.unwrap(self.placeholder)) {
            if (typeof ko.unwrap(self.placeholder) === 'string') {
                self.placeholder({
                    [self.currentLanguage()]: ko.unwrap(self.placeholder),
                });
            }
            self.currentPlaceholder(self.placeholder()[self.currentLanguage()]);
        }
    };

    init();

    self.currentDefaultText.subscribe(newValue => {
        const currentLanguage = self.currentDefaultLanguage();
        if(!currentLanguage) { return; }
        currentDefaultValue[currentLanguage].value = newValue;
        self.defaultValue(currentDefaultValue);
        self.card._card.valueHasMutated();
    });

    self.currentDefaultDirection.subscribe(newValue => {
        const currentLanguage = self.currentDefaultLanguage();
        if(!currentLanguage) { return; }
        if(!currentDefaultValue?.[currentLanguage]){
            currentDefaultValue[currentLanguage] = {};
        }
        currentDefaultValue[currentLanguage].direction = newValue;
        self.defaultValue(currentDefaultValue);
        self.card._card.valueHasMutated();
    });

    self.currentDefaultLanguage.subscribe(newValue => {
        if(!self.currentDefaultLanguage()){ return; }
        const currentLanguage = self.currentDefaultLanguage();
        if(!currentDefaultValue?.[currentLanguage]) {
            currentDefaultValue[currentLanguage] = {
                value: '',
                direction: self.languages().find(lang => lang.code === currentLanguage)?.default_direction
            };
            self.defaultValue(currentDefaultValue);
            self.card._card.valueHasMutated();
        }

        self.currentDefaultText(self.defaultValue()?.[currentLanguage]?.value);
        self.currentDefaultDirection(self.defaultValue()?.[currentLanguage]?.direction);

    });

    if (ko.isObservable(self.value)) {
        self.value.subscribe(newValue => {
            const currentLanguage = self.currentLanguage();
            if(!currentLanguage) { return; }
            if(JSON.stringify(currentValue) != JSON.stringify(ko.toJS(ko.unwrap(self.value)))){
                self.currentText(newValue?.[currentLanguage]?.value);
            }
        });
    }

    self.currentText.subscribe(newValue => {
        const currentLanguage = self.currentLanguage();
        if(!currentLanguage) { return; }

        if(!currentValue?.[currentLanguage]){
            currentValue[currentLanguage] = {};
        }
        currentValue[currentLanguage].value = newValue?.[currentLanguage] ? newValue[currentLanguage]?.value : newValue;
        
        if (ko.isObservable(self.value)) {
            self.value(currentValue);
        } else {
            self.value[currentLanguage].value(newValue);
        }
        
    });

    self.currentDirection.subscribe(newValue => {
        const currentLanguage = self.currentLanguage();
        if(!currentLanguage) { return; }

        if(!currentValue?.[currentLanguage]){
            currentValue[currentLanguage] = {};
        }
        currentValue[currentLanguage].direction = newValue;
        if (ko.isObservable(self.value)) {
            self.value(currentValue);
        } else {
            self.value[currentLanguage].direction(newValue);
        }
    });

    self.currentLanguage.subscribe(() => {
        if(!self.currentLanguage()){ return; }
        const currentLanguage = self.currentLanguage();

        self.currentText(koMapping.toJS(self.value)[currentLanguage]?.value);
        self.currentDirection(koMapping.toJS(self.value)[currentLanguage]?.direction);
        self.currentPlaceholder(koMapping.toJS(self.placeholder)[currentLanguage]);
    });

    self.currentPlaceholder.subscribe(newValue => {
        if(!self.currentLanguage()){ return; }
        const currentLanguage = self.currentLanguage();

        if (self.card && ko.isObservable(self.placeholder)) {
            const patchedPlaceholder = self.placeholder() || {};
            patchedPlaceholder[currentLanguage] = newValue;
            self.placeholder(patchedPlaceholder);
            self.card._card.valueHasMutated();
        }
    });
};

export default ko.components.register('text-widget', {
    viewModel: viewModel,
    template: textWidgetTemplate,
});
