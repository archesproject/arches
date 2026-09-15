import { describe, it, expect } from 'vitest';
import moment from 'moment';

import { componentsForFormat, VIEW_MODE_BY_LEGACY_NAME } from './datepicker-options.js';

/**
 * Covers the translation layer between the options stored in adopters' graph node
 * configs and Tempus Dominus' own.
 *
 * These are the values a modeller can actually pick, so they are the contract that
 * has to survive replacing eonasdan-bootstrap-datetimepicker. Getting this wrong
 * shows up as a date field offering the wrong picker, or silently reformatting
 * stored data.
 */

/** The four formats offered by views/components/datatypes/date.js. */
const STORED_FORMATS = [
    'YYYY-MM-DD HH:mm:ssZ',
    'YYYY-MM-DD',
    'YYYY-MM',
    'YYYY',
];

describe('componentsForFormat', () => {
    it('offers a clock only when the format carries a time', () => {
        expect(componentsForFormat('YYYY-MM-DD HH:mm:ssZ').clock).toBe(true);
        expect(componentsForFormat('YYYY-MM-DD').clock).toBe(false);
        expect(componentsForFormat('YYYY-MM').clock).toBe(false);
        expect(componentsForFormat('YYYY').clock).toBe(false);
    });

    it('offers day selection only when the format carries a day', () => {
        expect(componentsForFormat('YYYY-MM-DD').date).toBe(true);
        expect(componentsForFormat('YYYY-MM').date).toBe(false);
        expect(componentsForFormat('YYYY').date).toBe(false);
    });

    it('offers month selection only when the format carries a month', () => {
        expect(componentsForFormat('YYYY-MM').month).toBe(true);
        expect(componentsForFormat('YYYY').month).toBe(false);
    });

    it('enables seconds and minutes independently', () => {
        const full = componentsForFormat('YYYY-MM-DD HH:mm:ssZ');
        expect(full.minutes).toBe(true);
        expect(full.seconds).toBe(true);

        const dateOnly = componentsForFormat('YYYY-MM-DD');
        expect(dateOnly.minutes).toBe(false);
        expect(dateOnly.seconds).toBe(false);
    });

    it('always leaves the year and calendar reachable', () => {
        for (const format of STORED_FORMATS) {
            const components = componentsForFormat(format);
            expect(components.year, format).toBe(true);
            expect(components.calendar, format).toBe(true);
        }
    });

    it('does not throw on a missing format', () => {
        expect(() => componentsForFormat(undefined)).not.toThrow();
        expect(componentsForFormat(undefined).clock).toBe(false);
    });
});

describe('VIEW_MODE_BY_LEGACY_NAME', () => {
    it('maps every legacy view mode the datepicker widget offers', () => {
        // From views/components/widgets/datepicker.js viewModeOptions.
        for (const legacy of ['decades', 'years', 'months', 'days']) {
            expect(VIEW_MODE_BY_LEGACY_NAME[legacy], legacy).toBeTruthy();
        }
    });

    it("renames only 'days', which Tempus Dominus calls 'calendar'", () => {
        expect(VIEW_MODE_BY_LEGACY_NAME.days).toBe('calendar');
        expect(VIEW_MODE_BY_LEGACY_NAME.months).toBe('months');
        expect(VIEW_MODE_BY_LEGACY_NAME.years).toBe('years');
        expect(VIEW_MODE_BY_LEGACY_NAME.decades).toBe('decades');
    });
});

describe('stored value round-tripping', () => {
    it('preserves every stored format, including the UTC offset Tempus Dominus cannot render', () => {
        // This is why moment stays the formatter: 'Z' has no Tempus Dominus token,
        // so letting it format would silently drop the offset from stored data.
        const date = new Date(Date.UTC(2026, 8, 14, 13, 45, 30));

        for (const format of STORED_FORMATS) {
            const written = moment(date).format(format);
            const readBack = moment(written, format);
            expect(readBack.isValid(), format).toBe(true);
            expect(moment(readBack.toDate()).format(format), format).toBe(written);
        }
    });

    it('keeps the offset token in the full ISO format', () => {
        const written = moment(new Date()).format('YYYY-MM-DD HH:mm:ssZ');
        expect(written).toMatch(/[+-]\d{2}:\d{2}$/);
    });
});
