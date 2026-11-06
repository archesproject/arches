import $ from 'jquery';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import _ from 'underscore';
import WidgetViewModel from 'viewmodels/widget';
import arches from 'arches';
import richTextWidgetTemplate from 'templates/views/components/widgets/rich-text.htm';
import 'bindings/ckeditor';
import 'bindings/select2-query';


/**
* registers a rich-text-widget component for use in forms
* @function external:"ko.components".rich-text-widget
* @param {object} params
* @param {string} params.value - the value being managed
* @param {function} params.config - observable containing config object
*/

const viewModel = function(params) {
    params.configKeys = ['placeholder', 'displayfullvalue'];
    const self = this;
    self.card = params.card;

    WidgetViewModel.apply(self, [params]);
    const initialCurrent = {};
    self.showi18nOptions = ko.observable(false);
    initialCurrent[arches.activeLanguage] = {value: '', direction: 'ltr'};
    const currentLanguage = arches.activeLanguage;
    let currentValue = koMapping.toJS(self.value) || initialCurrent;
    self.currentLanguage = ko.observable(currentLanguage);
    self.currentPlaceholder = ko.observable();
    let updating = false;

    if(self.form){
        self.form.on('tile-reset', (x) => {
            if (ko.unwrap(self.value)) {
                currentValue = koMapping.toJS(self.value);
                self.currentText(currentValue[self.currentLanguage()]?.value);
                self.currentDirection(currentValue[self.currentLanguage()]?.direction);
            }
        });
    }

    const languages = arches.languages;
    self.languages =  ko.observableArray(languages);
    self.currentLanguage(languages.find(element => element.code == arches.activeLanguage)?.code);

    if(!currentValue?.[currentLanguage]){
        self.currentText = ko.observable('');
        self.currentDirection = ko.observable('ltr');
        currentValue[currentLanguage] = {value: '', direction: 'ltr'};
    } else {
        self.currentText = ko.observable(currentValue?.[currentLanguage]?.value);
        self.currentDirection = ko.observable(ko.unwrap(currentValue?.[currentLanguage]?.direction));
    }

    if (ko.unwrap(self.placeholder)) {
        if (typeof ko.unwrap(self.placeholder) === 'string') {
            self.placeholder({
                [self.currentLanguage()]: ko.unwrap(self.placeholder),
            });
        }
        self.currentPlaceholder(self.placeholder()[self.currentLanguage()]);
    }

    self.defaultText = ko.observable();
    self.defaultText.subscribe(newValue => {
        const config = self.config();
        config.placeholder = newValue;
        self.config(config);
    });

    const valueLeaf = self.value?.[arches.activeLanguage]?.value || self.value;
    valueLeaf?.subscribe(newValue => {
        const currentLanguage = self.currentLanguage();
        if(!currentLanguage) { return; }

        if(!updating && (JSON.stringify(currentValue) != JSON.stringify(ko.toJS(ko.unwrap(self.value))))){
            // Don't attempt to update currentText if we are in the middle of another update.
            // currentValue will already be correct, and self.value has not yet finished updating.
            // https://github.com/archesproject/arches/issues/10468
            self.currentText(newValue?.[currentLanguage]?.value || newValue);
        }
    });

    self.currentText.subscribe(newValue => {
        const currentLanguage = self.currentLanguage();
        if(!currentLanguage) { return; }

        updating = true;
        if(!currentValue?.[currentLanguage]){
            currentValue[currentLanguage] = {};
        }
        currentValue[currentLanguage].value = newValue?.[currentLanguage] ? newValue[currentLanguage]?.value : newValue;
        if (ko.isObservable(self.value)) {
            self.value(currentValue);
        } else {
            self.value[currentLanguage].value(newValue);
        }
        updating = false;
    });
    self.currentDirection.subscribe(newValue => {
        const currentLanguage = self.currentLanguage();
        if(!currentLanguage) { return; }

        updating = true;
        if(!currentValue?.[currentLanguage]){
            currentValue[currentLanguage] = {};
        }
        currentValue[currentLanguage].direction = newValue;

        if (ko.isObservable(self.value)) {
            self.value(currentValue);
        } else {
            self.value[currentLanguage].direction(newValue);
        }
        updating = false;
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
            const patchedPlaceholder = self.placeholder();
            patchedPlaceholder[currentLanguage] = newValue;
            self.placeholder(patchedPlaceholder);
            self.card._card.valueHasMutated();
        }
    });

    this.displayfullvalue(params.displayfullvalue);
};

export default ko.components.register('rich-text-widget', {
    viewModel: viewModel,
    template: richTextWidgetTemplate,
});
