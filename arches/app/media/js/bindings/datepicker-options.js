/**
 * Translates the date picker options stored in graph node configs into the shape
 * Tempus Dominus 6 expects.
 *
 * Kept apart from the binding itself because these are pure functions over values
 * that live in adopters' databases — they are the part of the
 * eonasdan-bootstrap-datetimepicker replacement most worth testing, and importing
 * them should not drag in the picker.
 *
 * See arches/app/media/js/bindings/datepicker.js.
 */

/** Legacy view names mapped onto Tempus Dominus' own. Only `days` differs. */
export const VIEW_MODE_BY_LEGACY_NAME = {
    days: 'calendar',
    months: 'months',
    years: 'years',
    decades: 'decades',
};

/**
 * Which pickers to show, derived from the moment format rather than configured
 * separately. A `YYYY` field should not offer a clock, and a `YYYY-MM` field should
 * not offer days.
 */
export function componentsForFormat(format) {
    const pattern = String(format || '');
    const hasDay = /D/.test(pattern);
    const hasMonth = /M/.test(pattern);
    const hasTime = /[Hhms]/.test(pattern);

    return {
        calendar: true,
        date: hasDay,
        month: hasMonth,
        year: true,
        decades: true,
        clock: hasTime,
        hours: hasTime,
        minutes: /m/.test(pattern),
        seconds: /s/.test(pattern),
    };
}
