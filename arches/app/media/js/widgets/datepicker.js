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
     * @param {boolean} params.value - the value being managed
     * @param {object} params.config -
     * @param {string} params.config.label - label to use alongside the text input
     * @param {string} params.config.minDate - Minimum date allowed to be chosen
     * @param {string} params.config.maxDate - Maximum date allowed to be chosen
     * @param {string} params.config.viewMode - The default view to display when the picker is shown. (Accepts: 'decades','years','months','days')
     * @param {string} params.config.dateFormat - Format of the date to display. (See moment.js' options for format: http://momentjs.com/docs/#/displaying/format/)
     */
    return ko.components.register('datepicker-widget', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['minDate', 'maxDate', 'viewMode', 'dateFormat'];
            WidgetViewModel.apply(this, [params]);

            // this.maxDateVal = this.maxDate() !== false ? moment(this.maxDate()).format(this.dateFormat()) : null;
            // this.minDateVal = this.minDate() !== false ? moment(this.minDate()).format(this.dateFormat()) : null;

            this.minDate.subscribe(function(val) {
                // if minDate is > max date
                // Set max date to >= min date
                console.log('before change:')
                console.log(this.minDate())
                console.log(this.maxDate())

                if (this.maxDate()!==false) {
                    if (this.maxDate()<this.minDate()){
                        this.maxDate(this.minDate())
                    }
                }
                console.log('after change:')
                console.log(this.minDate())
                console.log(this.maxDate())
                // this.maxDate() !== false && this.maxDate() < this.minDate() ? this.maxDate(this.minDate()) : null;
            }, this)

            this.maxDate.subscribe(function(val) {
                this.minDate() !== false && this.minDate() < this.maxDate() ? this.minDate(this.maxDate()) : null;
            }, this)

            this.placeholder = params.config().placeholder;

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

            // these options should be set in the global admin page
            this.dateFormatOptions = ko.observableArray([{
                'id': 'YYYY-MM-DD',
                'name': 'ISO 8601 (YYYY-MM-DD)'
            }, {
                'id': 'YYYY-MM',
                'name': 'ISO 8601 Month (YYYY-MM)'
            }, {
                'id': 'YYYY',
                'name': 'CE Year (YYYY)'
            }]);

            this.onViewModeSelection = function(val, e) {
                this.viewMode(e.currentTarget.value)
            };

            this.onDateFormatSelection = function(val, e) {
                this.dateFormat(e.currentTarget.value)
            };
        },
        template: {
            require: 'text!widget-templates/datepicker'
        }
    });
});
