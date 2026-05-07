import ko from 'knockout';
import _ from 'underscore';
import { TempusDominus, DateTime } from 'bootstrap-datetimepicker';

var viewModeMap = {
    days: 'calendar',
    months: 'months',
    years: 'years',
    decades: 'decades'
};

function momentToTDFormat(fmt) {
    if (!fmt) return 'yyyy-MM-dd';
    return fmt
        .replace(/YYYY/g, 'yyyy')
        .replace(/YY/g, 'yy')
        .replace(/DD/g, 'dd')
        .replace(/D/g, 'd')
        .replace(/A/g, 'T');
}

function toDateTime(val) {
    if (!val || val === false) return undefined;
    if (val instanceof Date) return new DateTime(val);
    var d = new Date(val);
    if (isNaN(d.getTime())) return undefined;
    return new DateTime(d);
}

ko.bindingHandlers.datepicker = {
    init: function (element, valueAccessor, allBindingsAccessor) {
        var options = valueAccessor() || {};
        var value = allBindingsAccessor().value;
        var minDateObs, maxDateObs, viewModeObs;

        _.forEach(options, function (v, key) {
            if (ko.isObservable(v)) {
                if (key === 'minDate') minDateObs = v;
                else if (key === 'maxDate') maxDateObs = v;
                else if (key === 'viewMode') viewModeObs = v;
            }
        });

        var format = ko.unwrap(options.format) || 'YYYY-MM-DD';
        var tdFormat = momentToTDFormat(format);
        var rawViewMode = ko.unwrap(options.viewMode) || 'days';
        var hasTime = /[Hh]/.test(format);

        var restrictions = {
            minDate: toDateTime(ko.unwrap(options.minDate)),
            maxDate: toDateTime(ko.unwrap(options.maxDate)),
        };

        var tdOptions = {
            localization: { format: tdFormat },
            display: {
                viewMode: viewModeMap[rawViewMode] || rawViewMode || 'calendar',
                icons: {
                    type: 'icons',
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down',
                    previous: 'fa fa-chevron-left',
                    next: 'fa fa-chevron-right',
                    today: 'fa fa-crosshairs',
                    clear: 'fa fa-trash',
                    close: 'fa fa-times',
                },
                components: {
                    clock: hasTime,
                },
            },
            restrictions: restrictions,
            allowInputToggle: true,
            keepInvalid: !!options.keepInvalid,
        };

        var picker = new TempusDominus(element, tdOptions);

        var currentVal = ko.isObservable(value) ? value() : value;
        if (currentVal && currentVal !== 'Date of Data Entry') {
            try { picker.dates.setFromInput(currentVal, 0); }
            catch (e) { /* invalid date */ }
        }

        var updating = false;

        if (ko.isObservable(value)) {
            value.subscribe(function (val) {
                if (updating) return;
                updating = true;
                try {
                    if (val && val !== 'Date of Data Entry') {
                        picker.dates.setFromInput(val, 0);
                    } else {
                        picker.dates.clear();
                    }
                } catch (e) { /* ignore */ }
                updating = false;
            });
        }

        if (minDateObs && ko.isObservable(minDateObs)) {
            minDateObs.subscribe(function (newVal) {
                restrictions.minDate = toDateTime(newVal);
                if (maxDateObs && ko.isObservable(maxDateObs) && maxDateObs() &&
                    newVal && new Date(maxDateObs()) < new Date(newVal)) {
                    maxDateObs(newVal);
                }
                picker.updateOptions({ restrictions: restrictions });
            });
        }

        if (maxDateObs && ko.isObservable(maxDateObs)) {
            maxDateObs.subscribe(function (newVal) {
                restrictions.maxDate = toDateTime(newVal);
                if (minDateObs && ko.isObservable(minDateObs) && minDateObs() &&
                    newVal && new Date(minDateObs()) > new Date(newVal)) {
                    minDateObs(newVal);
                }
                picker.updateOptions({ restrictions: restrictions });
            });
        }

        if (viewModeObs && ko.isObservable(viewModeObs)) {
            viewModeObs.subscribe(function (newVal) {
                var mapped = viewModeMap[newVal] || newVal || 'calendar';
                picker.updateOptions({ display: { viewMode: mapped } });
            });
        }

        element.addEventListener('change.td', function (event) {
            if (updating) return;
            updating = true;
            if (ko.isObservable(value)) {
                if (event.detail.isClear || !event.detail.date) {
                    value(null);
                } else {
                    value(element.value);
                }
            }
            updating = false;
        });

        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            picker.dispose();
        });
    }
};

ko.bindingHandlers.datepicker.init = ko.bindingHandlers.datepicker.init.bind(ko.bindingHandlers.datepicker);

export default ko.bindingHandlers.datepicker;
