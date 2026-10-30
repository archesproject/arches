/**
 * Translates the date picker options stored in graph node configs into the shape Tempus
 * Dominus 6 expects. Kept apart from bindings/datepicker.js so importing them does not
 * drag in the picker.
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
 * separately: a `YYYY` field should not offer a clock, nor a `YYYY-MM` field days.
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
