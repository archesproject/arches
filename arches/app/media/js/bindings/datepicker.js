import _ from 'underscore';
import ko from 'knockout';
import moment from 'moment';
import { TempusDominus } from 'bootstrap-datetimepicker';

import { componentsForFormat, VIEW_MODE_BY_LEGACY_NAME } from './datepicker-options.js';

/**
 * Date picker binding, replacing eonasdan-bootstrap-datetimepicker 4.17.49.
 *
 * That package is Bootstrap 3-only and has had no release since 2017. Its successor
 * by the same author, Tempus Dominus 6, is a standalone rewrite with no Bootstrap
 * dependency at all — so this binding keeps working unchanged across the Bootstrap 5
 * upgrade.
 *
 * ## The contract this must not break
 *
 * `format` and `viewMode` are stored in graph node configs in adopters' databases:
 * `YYYY-MM-DD HH:mm:ssZ`, `YYYY-MM-DD`, `YYYY-MM`, `YYYY` for the former, and
 * `days` / `months` / `years` / `decades` for the latter. Those are moment tokens and
 * legacy view names, and they cannot be migrated away from without touching every
 * deployment's data. So the binding's public options stay exactly as they were and
 * are translated internally:
 *
 *     data-bind="datepicker: {format: dateFormat, viewMode: viewMode,
 *                             minDate: minDate, maxDate: maxDate}, value: value"
 *
 * ## Why moment still does the formatting
 *
 * Tempus Dominus formats through `Intl.DateTimeFormat` and has no token for a UTC
 * offset, so it cannot render `YYYY-MM-DD HH:mm:ssZ` — one of the four formats a
 * modeller can pick. Rather than degrade that format, Tempus Dominus is used purely
 * as the calendar UI and moment remains the single authority for turning a date into
 * the stored string and back. moment is already a core dependency, and this keeps the
 * value written to the observable byte-identical to what the old binding wrote.
 */

/** Parses a stored value with the format that produced it; null when unusable. */
function parseStoredValue(value, format) {
    if (value === null || value === undefined || value === '') {
        return null;
    }
    if (value instanceof Date) {
        return value;
    }
    const parsed = moment(value, format);
    return parsed.isValid() ? parsed.toDate() : null;
}

function toDateOrNull(value, format) {
    if (value === false || value === null || value === undefined || value === '') {
        return null;
    }
    return parseStoredValue(value, format);
}

ko.bindingHandlers.datepicker = {
    init: function (element, valueAccessor, allBindingsAccessor) {
        const options = ko.unwrap(valueAccessor()) || {};
        const format = ko.unwrap(options.format);
        const valueObservable = allBindingsAccessor().value;

        // Guards the two-way sync between the observable and the picker.
        let synchronizing = false;

        function buildPickerOptions() {
            const legacyViewMode = ko.unwrap(options.viewMode);
            const restrictions = {};

            const minDate = toDateOrNull(ko.unwrap(options.minDate), format);
            const maxDate = toDateOrNull(ko.unwrap(options.maxDate), format);
            if (minDate) {
                restrictions.minDate = minDate;
            }
            if (maxDate) {
                restrictions.maxDate = maxDate;
            }

            return {
                keepInvalid: !!ko.unwrap(options.keepInvalid),
                restrictions: restrictions,
                display: {
                    viewMode: VIEW_MODE_BY_LEGACY_NAME[legacyViewMode] || 'calendar',
                    components: componentsForFormat(format),
                    buttons: { today: true, clear: true, close: true },
                },
            };
        }

        const picker = new TempusDominus(element, buildPickerOptions());

        /** Writes the moment-formatted string to both the input and the observable. */
        function publish(date) {
            const formatted = date ? moment(date).format(format) : null;
            synchronizing = true;
            element.value = formatted || '';
            if (ko.isObservable(valueObservable)) {
                valueObservable(formatted);
            }
            synchronizing = false;
        }

        const initialDate = parseStoredValue(
            ko.isObservable(valueObservable) ? valueObservable() : null,
            format
        );
        if (initialDate) {
            picker.dates.setValue(picker.dates.parseInput(initialDate));
            element.value = moment(initialDate).format(format);
        }

        element.addEventListener('change.td', function (event) {
            if (synchronizing) {
                return;
            }
            const date = event.detail && event.detail.date ? new Date(event.detail.date) : null;
            publish(date);
        });

        // `keepInvalid` exists so the time filter can hold a partial date the user is
        // still typing; without it the picker would clear the field mid-keystroke.
        if (ko.unwrap(options.keepInvalid)) {
            element.addEventListener('input', function () {
                if (synchronizing || !ko.isObservable(valueObservable)) {
                    return;
                }
                synchronizing = true;
                valueObservable(element.value || null);
                synchronizing = false;
            });
        }

        const subscriptions = [];

        if (ko.isObservable(valueObservable)) {
            subscriptions.push(valueObservable.subscribe(function (newValue) {
                if (synchronizing || newValue === 'Date of Data Entry') {
                    return;
                }
                const date = parseStoredValue(newValue, format);
                synchronizing = true;
                if (date) {
                    picker.dates.setValue(picker.dates.parseInput(date));
                    element.value = moment(date).format(format);
                } else {
                    picker.dates.clear();
                    element.value = '';
                }
                synchronizing = false;
            }));
        }

        // minDate and maxDate are observables on the widget config forms, so the
        // picker's restrictions have to follow them. The old binding also coerced one
        // bound past the other; that is kept.
        const minDateObservable = ko.isObservable(options.minDate) ? options.minDate : null;
        const maxDateObservable = ko.isObservable(options.maxDate) ? options.maxDate : null;

        function reconcileBounds(changedKey, newValue) {
            if (!minDateObservable || !maxDateObservable || !newValue) {
                return;
            }
            const min = minDateObservable();
            const max = maxDateObservable();
            if (!min || !max) {
                return;
            }
            if (moment(min, format).isAfter(moment(max, format))) {
                if (changedKey === 'minDate') {
                    maxDateObservable(min);
                } else {
                    minDateObservable(max);
                }
            }
        }

        _.each({ minDate: minDateObservable, maxDate: maxDateObservable }, function (observable, key) {
            if (!observable) {
                return;
            }
            subscriptions.push(observable.subscribe(function (newValue) {
                reconcileBounds(key, newValue);
                picker.updateOptions(buildPickerOptions());
            }));
        });

        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            subscriptions.forEach(function (subscription) {
                subscription.dispose();
            });
            picker.dispose();
        });
    }
};

ko.bindingHandlers.datepicker.init = ko.bindingHandlers.datepicker.init.bind(ko.bindingHandlers.datepicker);

export default ko.bindingHandlers.datepicker;
