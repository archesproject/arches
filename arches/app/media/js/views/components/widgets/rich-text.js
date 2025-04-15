import $ from 'jquery';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import _ from 'underscore';
import WidgetViewModel from 'viewmodels/widget';
import arches from 'arches';
import richTextWidgetTemplate from 'templates/views/components/widgets/rich-text.htm';
import 'bindings/ckeditor';
import 'bindings/chosen';


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
    const currentLanguage = {"code": arches.activeLanguage};
    let currentValue = koMapping.toJS(self.value) || initialCurrent;
    self.currentLanguage = ko.observable(currentLanguage);
    self.currentPlaceholder = ko.observable();
    let updating = false;

    if(self.form){
        self.form.on('tile-reset', (x) => {
            if (ko.unwrap(self.value)) {
                currentValue = koMapping.toJS(self.value);
                self.currentText(currentValue[self.currentLanguage().code]?.value);
                self.currentDirection(currentValue[self.currentLanguage().code]?.direction);
            }
        });
    }

    const languages = arches.languages;
    self.languages =  ko.observableArray(languages);
    self.currentLanguage(languages.find(element => element.code == arches.activeLanguage));

    if(!currentValue?.[currentLanguage.code]){
        self.currentText = ko.observable('');
        self.currentDirection = ko.observable('ltr');
        currentValue[currentLanguage.code] = {value: '', direction: 'ltr'};
    } else {
        self.currentText = ko.observable(currentValue?.[currentLanguage.code]?.value);
        self.currentDirection = ko.observable(ko.unwrap(currentValue?.[currentLanguage.code]?.direction));
    }

    if (ko.unwrap(self.placeholder)) {
        if (typeof ko.unwrap(self.placeholder) === 'string') {
            self.placeholder({
                [self.currentLanguage().code]: ko.unwrap(self.placeholder),
            });
        }
        self.currentPlaceholder(self.placeholder()[self.currentLanguage().code]);
    }

    self.strippedValue = ko.pureComputed(() => {
        return $(`<span>${self.currentText()}</span>`).text();
    });

    self.strippedValue();

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
            self.currentText(newValue?.[currentLanguage.code]?.value || newValue);
        }
    });

    self.currentText.subscribe(newValue => {
        const currentLanguage = self.currentLanguage();
        if(!currentLanguage) { return; }

        updating = true;
        if(!currentValue?.[currentLanguage.code]){
            currentValue[currentLanguage.code] = {};
        }
        currentValue[currentLanguage.code].value = newValue?.[currentLanguage.code] ? newValue[currentLanguage.code]?.value : newValue;
        if (ko.isObservable(self.value)) {
            self.value(currentValue);
        } else {
            self.value[currentLanguage.code].value(newValue);
        }
        updating = false;
    });
    self.currentDirection.subscribe(newValue => {
        const currentLanguage = self.currentLanguage();
        if(!currentLanguage) { return; }

        updating = true;
        if(!currentValue?.[currentLanguage.code]){
            currentValue[currentLanguage.code] = {};
        }
        currentValue[currentLanguage.code].direction = newValue;

        if (ko.isObservable(self.value)) {
            self.value(currentValue);
        } else {
            self.value[currentLanguage.code].direction(newValue);
        }
        updating = false;
    });

    self.currentLanguage.subscribe(() => {
        if(!self.currentLanguage()){ return; }

        const currentLanguage = self.currentLanguage();

        self.currentText(koMapping.toJS(self.value)[currentLanguage.code]?.value);
        self.currentDirection(koMapping.toJS(self.value)[currentLanguage.code]?.direction);
        self.currentPlaceholder(koMapping.toJS(self.placeholder)[currentLanguage.code]);
    });

    self.currentPlaceholder.subscribe(newValue => {
        if(!self.currentLanguage()){ return; }
        const currentLanguage = self.currentLanguage();

        if (self.card && ko.isObservable(self.placeholder)) {
            const patchedPlaceholder = self.placeholder();
            patchedPlaceholder[currentLanguage.code] = newValue;
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
