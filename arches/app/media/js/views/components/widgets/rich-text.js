define([
    'jquery',
    'knockout', 
    'knockout-mapping',
    'underscore', 
    'viewmodels/widget', 
    'arches', 
    'templates/views/components/widgets/rich-text.htm',
    'bindings/ckeditor', 
    'bindings/chosen'
], function($, ko, koMapping, _, WidgetViewModel, arches, richTextWidgetTemplate) {
    /**
    * registers a rich-text-widget component for use in forms
    * @function external:"ko.components".rich-text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    */

    const viewModel = function(params) {
        params.configKeys = ['displayfullvalue'];
        const self = this;
         
        WidgetViewModel.apply(self, [params]);
        const initialCurrent = {};
        self.showi18nOptions = ko.observable(false);
        initialCurrent[arches.activeLanguage] = {value: '', direction: 'ltr'};
        const currentLanguage = {"code": arches.activeLanguage};
        let currentValue = koMapping.toJS(self.value);
        self.currentLanguage = ko.observable(currentLanguage);

        if(self.form){
            self.form.on('tile-reset', (x) => {
                currentValue = koMapping.toJS(self.value);
                self.currentText(currentValue[self.currentLanguage().code]?.value);
                self.currentDirection(currentValue[self.currentLanguage().code]?.direction);
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

        self.strippedValue = ko.pureComputed(() => {
            return $(`<span>${self.currentText()}</span>`).text();
        });

        self.strippedValue();
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

        this.displayfullvalue(params.displayfullvalue);
    };

    return ko.components.register('rich-text-widget', {
        viewModel: viewModel,
        template: richTextWidgetTemplate,
    });
});
