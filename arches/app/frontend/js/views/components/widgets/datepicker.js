define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'moment',
    'bindings/datepicker',
    'bindings/moment-date',
    'bindings/chosen'
], function(ko, _, WidgetViewModel, arches, moment) {
    /**
     * registers a datepicker-widget component for use in forms
     * @function external:"ko.components".datepicker-widget
     * @param {object} params
     * @param {date} params.value - the value being managed
     * @param {object} params.config -
     * @param {string} params.config.label - label to use alongside the text input
     * @param {string} params.config.minDate - Minimum date allowed to be chosen
     * @param {string} params.config.maxDate - Maximum date allowed to be chosen
     * @param {string} params.config.viewMode - The default view to display when the picker is shown. (Accepts: 'decades','years','months','days')
     * @param {string} params.config.dateFormat - Format of the date to display. (See moment.js' options for format: http://momentjs.com/docs/#/displaying/format/)
     */

    var DatePickerWidget = function(params) {
        var self = this;
        params.configKeys = ['minDate', 'maxDate', 'viewMode', 'dateFormat', 'defaultValue'];
        WidgetViewModel.apply(this, [params]);

        if (self.node.config && ko.unwrap(self.node.config.dateFormat)) {
            this.dateFormat(ko.unwrap(self.node.config.dateFormat));
        }
        if (!ko.unwrap(this.dateFormat)) {
            this.dateFormat = ko.observable(self.node.datatypeLookup.date.config);
        } 

        this.placeholder = this.config().placeholder;
        this.viewModeOptions = ko.observableArray([{
            'id': 'days',
            'name': 'Days'
        }, {
            'id': 'months',
            'name': 'Months'
        }, {
            'id': 'years',
            'name': 'Years'
        }, {
            'id': 'decades',
            'name': 'Decades'
        }]);

        this.onViewModeSelection = function(val, e) {
            this.viewMode(e.currentTarget.value);
        };

        this.on = this.config().on || 'Date of Data Entry';
        this.off = this.config().off || '';
        this.setvalue = this.config().setvalue || function(self){
            if(self.defaultValue() === self.on){
                self.defaultValue(self.off);
            }else{
                self.defaultValue(self.on);
            }
        };

        this.setdefault = this.config().setdefault || function(self){
            if(self.defaultValue() === self.on){
                self.defaultValue(self.off);
            }else{
                self.defaultValue(self.on);
            }
        };

        this.getdefault = this.config().getdefault || ko.computed(function(){
            return this.defaultValue() == this.on;
        }, this);

        if (self.form && this.defaultValue() === 'Date of Data Entry') {
            if (this.value() === 'Date of Data Entry') {
                var today = new Date();
                var dd = today.getDate();
                var mm = today.getMonth()+1;
                var yyyy = today.getFullYear();
                if(dd<10) {
                    dd = '0'+dd;
                }
                if(mm<10) {
                    mm = '0'+mm;
                }
                today = yyyy + '-' + mm + '-' + dd;
                self.value(today);
            }
        }

        this.disposables.push(this.getdefault);
    };

    return ko.components.register('datepicker-widget', {
        viewModel: DatePickerWidget,
        template: {
            require: 'text!widget-templates/datepicker'
        }
    });
});
